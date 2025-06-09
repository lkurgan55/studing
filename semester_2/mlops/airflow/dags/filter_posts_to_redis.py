from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import json
import pandas as pd
import redis
import joblib
from minio import Minio
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, REDIS_URL, TMP_DIR, MODEL_BUCKET, MODEL_DIR, ENCODER_FILE
from utils import download_from_minio
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

default_args = {
    'start_date': datetime(2024, 1, 1),
}


def download_model(**kwargs):
    """Load the current model from MinIO."""
    model_path = f"{TMP_DIR}/current_model"
    download_from_minio(
        bucket=MODEL_BUCKET,
        prefix_or_key="current_model",
        dest_dir=model_path,
        recursive=True
    )
    print(f"Model downloaded to {model_path}")


def load_posts_from_minio(**kwargs):
    """Load preprocessed posts from MinIO and push to XCom."""
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

    obj = client.get_object(bucket_name="preprocessed", object_name="cleaned_posts.json")
    content = obj.read().decode('utf-8')
    posts = json.loads(content)

    kwargs["ti"].xcom_push(key="posts", value=posts)


def filter_to_redis(**context):
    """Фільтрує пости за допомогою моделі та зберігає 'other' у Redis."""
    posts = context['ti'].xcom_pull(task_ids='load_posts')
    df = pd.DataFrame(posts)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, device=0)

    label_encoder = joblib.load(ENCODER_FILE)

    raw_preds = classifier(df['text'].tolist(), truncation=True)

    pred_labels = [label_encoder.inverse_transform([int(pred['label'].split('_')[-1])])[0] for pred in raw_preds]
    df['label'] = pred_labels

    df_other = df[df['label'] == 'other']

    r = redis.from_url(REDIS_URL)
    r.set('top_posts', df_other.to_json(orient='records'))

    print(f"Saved {len(df_other)} 'other' posts to Redis")


dag = DAG(
    'filter_to_redis',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
)

with dag:
    load_posts_task = PythonOperator(
        task_id='load_posts',
        python_callable=load_posts_from_minio
    )

    download_model_task = PythonOperator(
        task_id='load_model',
        python_callable=download_model
    )

    filter_to_redis_task = PythonOperator(
        task_id='filter_to_redis',
        python_callable=filter_to_redis,
        provide_context=True
    )

    [download_model_task, load_posts_task] >> filter_to_redis_task

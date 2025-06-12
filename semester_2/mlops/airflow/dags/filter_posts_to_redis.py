from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import json
import pandas as pd
import redis
import joblib
from minio import Minio
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, REDIS_URL, TMP_DIR, MODEL_BUCKET, ENCODER_FILE, DATA_BUCKET
from utils import download_from_minio
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification


date_prefix = datetime.utcnow().strftime("%Y-%m-%d")

client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

MODEL_PATH = f"{TMP_DIR}/current_model"


def download_model(**kwargs):
    """Load the current model from MinIO."""
    download_from_minio(
        bucket=MODEL_BUCKET,
        prefix_or_key="current_model",
        dest_dir=MODEL_PATH,
        recursive=True
    )

    download_from_minio(
        bucket=MODEL_BUCKET,
        prefix_or_key=ENCODER_FILE,
        dest_dir=MODEL_PATH,
        recursive=True
    )

    print(f"Model and encoder downloaded to {MODEL_PATH}")


def load_posts_from_minio(**kwargs):
    """Load preprocessed posts from MinIO and push to XCom."""

    obj = client.get_object(bucket_name=DATA_BUCKET, object_name=f"processed_data/{date_prefix}/cleaned_posts.json")
    content = obj.read().decode('utf-8')
    posts = json.loads(content)

    kwargs["ti"].xcom_push(key="posts", value=posts)


def filter_posts(**context):
    """Filter posts to 'other' category and save to Redis."""
    posts = context['ti'].xcom_pull(task_ids='load_posts', key='posts')
    df = pd.DataFrame(posts)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

    label_encoder = joblib.load(f"{MODEL_PATH}/{ENCODER_FILE}")

    raw_preds = classifier(df['text'].tolist(), truncation=True)

    pred_labels = [label_encoder.inverse_transform([int(pred['label'].split('_')[-1])])[0] for pred in raw_preds]
    df['label'] = pred_labels

    df_other = df[df['label'] == 'other']

    context['ti'].xcom_push(key='other_posts', value=df_other.to_dict(orient='records'))

    print(f"Saved {len(df_other)} 'other' posts to Redis")


def write_posts_redis(**context):
    """Write filtered posts to Redis."""
    posts = context['ti'].xcom_pull(task_ids='filter_posts', key='other_posts')

    r = redis.from_url(REDIS_URL)
    r.set('top_posts', json.dumps(posts))

    print("Saved 'other' posts to Redis")


default_args = {
    'start_date': datetime(2024, 1, 1),
}

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

    filter_post_task = PythonOperator(
        task_id='filter_posts',
        python_callable=filter_posts,
        provide_context=True
    )

    write_posts_redis_task = PythonOperator(
        task_id='write_posts_redis',
        python_callable=write_posts_redis,
        provide_context=True
    )

    [download_model_task, load_posts_task] >> filter_post_task >> write_posts_redis_task

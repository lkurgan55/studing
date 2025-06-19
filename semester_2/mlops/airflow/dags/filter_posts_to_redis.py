from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import json
import pandas as pd
import redis
import joblib
import mlflow
from minio import Minio
from config import REDIS_URL, MODEL_NAME, MODEL_ALIAS, MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, DATA_BUCKET
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification


def load_champion_model(**kwargs):
    """Load model and encoder from MLflow registry (champion version)."""
    model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
    local_path = mlflow.artifacts.download_artifacts(artifact_uri=model_uri)

    model_path = f"{local_path}/model"
    tokenizer_path = f"{local_path}/components/tokenizer"
    encoder_path = f"{local_path}/components/encoder/label_encoder.pkl"

    kwargs['ti'].xcom_push(key='model_path', value=model_path)
    kwargs['ti'].xcom_push(key='tokenizer_path', value=tokenizer_path)
    kwargs['ti'].xcom_push(key='encoder_path', value=encoder_path)


def load_posts_from_minio(**kwargs):
    """Load posts from MinIO bucket."""
    date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    obj = client.get_object(bucket_name=DATA_BUCKET, object_name=f"processed_data/{date_prefix}/cleaned_posts.json")
    content = obj.read().decode('utf-8')
    posts = json.loads(content)

    kwargs["ti"].xcom_push(key="posts", value=posts)


def filter_posts(**context):
    posts = context['ti'].xcom_pull(task_ids='load_posts', key='posts')
    model_path = context['ti'].xcom_pull(task_ids='load_model', key='model_path')
    tokenizer_path = context['ti'].xcom_pull(task_ids='load_model', key='tokenizer_path')
    encoder_path = context['ti'].xcom_pull(task_ids='load_model', key='encoder_path')

    df = pd.DataFrame(posts)

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

    label_encoder = joblib.load(encoder_path)
    id_to_label = {v: k for k, v in label_encoder.items()}

    raw_preds = classifier(df['text'].tolist(), truncation=True)

    pred_labels = [id_to_label[int(pred["label"].replace("LABEL_", ""))] for pred in raw_preds]

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
    catchup=False,
    tags=["mlflow", "filter"]
)

with dag:
    download_model_task = PythonOperator(
        task_id='load_model',
        python_callable=load_champion_model
    )

    load_posts_task = PythonOperator(
        task_id='load_posts',
        python_callable=load_posts_from_minio
    )

    filter_post_task = PythonOperator(
        task_id='filter_posts',
        python_callable=filter_posts
    )

    write_posts_redis_task = PythonOperator(
        task_id='write_posts_redis',
        python_callable=write_posts_redis
    )

    [download_model_task, load_posts_task] >> filter_post_task >> write_posts_redis_task

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from minio import Minio
from io import BytesIO
import json
import re
import string
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, DATA_BUCKET

date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
client = Minio(endpoint=MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

def clean_text(text):
    """Clean the text by removing URLs, mentions, hashtags, and unwanted characters."""
    text = text.lower()

    # Delete links, mentions, hashtags
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#\w+", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Keep only ASCII characters: letters, numbers, punctuation, spaces
    allowed = string.ascii_letters + string.digits + string.punctuation + " "
    text = ''.join(c for c in text if c in allowed)

    return text


def preprocess_posts(**context):
    """Load raw posts from MinIO, clean them, and push to XCom."""
    source_path = f"raw_data/twitter/{date_prefix}/tweets.json"

    response = client.get_object(DATA_BUCKET, source_path)
    posts = json.loads(response.read().decode("utf-8"))

    cleaned = [{"text": clean_text(p["text"])} for p in posts]

    context["ti"].xcom_push(key="cleaned_posts", value=cleaned)


def save_cleaned_posts(**context):
    """Save cleaned posts to MinIO."""
    cleaned = context["ti"].xcom_pull(key="cleaned_posts", task_ids="preprocess_posts")
    dest_path = f"processed_data/{date_prefix}/cleaned_posts.json"

    cleaned_bytes = json.dumps(cleaned, indent=2).encode("utf-8")
    client.put_object(
        DATA_BUCKET,
        dest_path,
        data=BytesIO(cleaned_bytes),
        length=len(cleaned_bytes),
        content_type="application/json"
    )

    print(f"Saved cleaned posts to {dest_path}")


default_args = {
    "start_date": datetime(2025, 1, 1),
}


with DAG(
    dag_id="preprocess_posts_to_minio",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["minio", "preprocessing"],
) as dag:

    preprocess_posts_task = PythonOperator(
        task_id="preprocess_posts",
        python_callable=preprocess_posts,
        provide_context=True,
    )

    save_cleaned_posts_task = PythonOperator(
        task_id="save_cleaned_posts",
        python_callable=save_cleaned_posts,
        provide_context=True,
    )

    preprocess_posts_task >> save_cleaned_posts_task

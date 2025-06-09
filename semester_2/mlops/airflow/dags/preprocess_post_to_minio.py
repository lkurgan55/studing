from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from minio import Minio
from io import BytesIO
import json
import re
import string
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, DATA_BUCKET


def clean_text(text):
    """Clean post text by removing unwanted characters and links."""
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


def preprocess_posts(**kwargs):
    """Preprocess text by cleaning text and saving to MinIO storage."""
    date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
    source_path = f"raw_data/twitter/{date_prefix}/tweets.json"
    dest_path = f"processed_data/twitter/{date_prefix}/cleaned_posts.json"

    client = Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    # Reading original text
    response = client.get_object(DATA_BUCKET, source_path)
    posts = json.loads(response.read().decode("utf-8"))

    # clean text
    cleaned = []
    for p in posts:
        cleaned.append({"text": clean_text(p["text"])})

    # write to MinIO
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

    preprocess = PythonOperator(
        task_id="preprocess_posts",
        python_callable=preprocess_posts,
        provide_context=True,
    )

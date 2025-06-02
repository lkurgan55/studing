from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from minio import Minio
import os
from io import BytesIO
import json
import re
import string
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, DATA_BUCKET


def clean_text(text):
    """Clean tweet text by removing unwanted characters and links."""
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


def preprocess_tweets(**kwargs):
    """Preprocess tweets by cleaning text and saving to MinIO storage."""
    date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
    source_path = f"raw_data/twitter/{date_prefix}/tweets.json"
    dest_path = f"processed_data/twitter/{date_prefix}/cleaned_tweets.json"

    client = Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    # Reading original tweets
    response = client.get_object(DATA_BUCKET, source_path)
    tweets = json.loads(response.read().decode("utf-8"))

    # clean text
    cleaned = []
    for t in tweets:
        cleaned.append({
            "id": t["id"],
            "text": clean_text(t["text"])
        })

    # write to MinIO
    cleaned_bytes = json.dumps(cleaned, indent=2).encode("utf-8")
    client.put_object(
        DATA_BUCKET,
        dest_path,
        data=BytesIO(cleaned_bytes),
        length=len(cleaned_bytes),
        content_type="application/json"
    )

    print(f"Saved cleaned tweets to {dest_path}")


default_args = {
    "start_date": datetime(2025, 1, 1),
}

with DAG(
    dag_id="preprocess_tweets_to_minio",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["twitter", "minio", "preprocessing"],
) as dag:

    preprocess = PythonOperator(
        task_id="preprocess_tweets",
        python_callable=preprocess_tweets,
        provide_context=True,
    )

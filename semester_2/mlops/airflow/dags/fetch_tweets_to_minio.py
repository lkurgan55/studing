from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import json
import tweepy
from minio import Minio
from io import BytesIO
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, TWITTER_BEARER_TOKEN


date_prefix = datetime.utcnow().strftime("%Y-%m-%d")


def fetch_tweets(**kwargs):
    """Fetch recent tweets related to news and politics."""
    client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
    query = "(news OR breaking OR politics OR war OR government OR parliament OR president OR conflict) -is:retweet lang:en"

    tweets = client.search_recent_tweets(query=query, max_results=100)

    data = []
    for tweet in tweets.data or []:
        data.append(
            {
                "id": tweet.id,
                "text": tweet.text
            }
        )

    kwargs["ti"].xcom_push(key="tweets", value=data)

def upload_to_minio(**kwargs):
    """Upload fetched tweets to MinIO storage."""
    tweets = kwargs["ti"].xcom_pull(task_ids="fetch_tweets", key="tweets")
    object_name = f"raw_data/twitter/{date_prefix}/tweets.json"

    client = Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    json_data = json.dumps(tweets, indent=2).encode("utf-8")
    client.put_object(
        "training-data",
        object_name,
        data=BytesIO(json_data),
        length=len(json_data),
        content_type="application/json"
    )
    print(f"Uploaded {object_name} to MinIO")

default_args = {
    "start_date": datetime(2025, 1, 1),
}

with DAG(
    dag_id="fetch_tweets_to_minio",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["twitter", "minio"],
) as dag:

    fetch = PythonOperator(
        task_id="fetch_tweets",
        python_callable=fetch_tweets,
        provide_context=True,
    )

    upload = PythonOperator(
        task_id="upload_to_minio",
        python_callable=upload_to_minio,
        provide_context=True,
    )

    fetch >> upload

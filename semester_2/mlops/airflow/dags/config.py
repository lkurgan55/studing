import os
from dotenv import load_dotenv

load_dotenv("/opt/airflow/.env")

MODEL_BUCKET = "model"
DATA_BUCKET = "training-data"
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "admin123")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
MODEL_BUCKET = "model"
DATA_BUCKET = "training-data"
TMP_DIR ='/tmp'
MODEL_DIR = "/tmp/model"
ENCODER_FILE = f"{MODEL_DIR}/label_encoder.pkl"

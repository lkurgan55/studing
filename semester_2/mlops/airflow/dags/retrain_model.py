
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from minio import Minio
from datasets import Dataset
import os
import json
import shutil
from pathlib import Path
import pickle
from transformers import Trainer, TrainingArguments, AutoModelForSequenceClassification, AutoTokenizer
from sklearn.preprocessing import LabelEncoder
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY

default_args = {
    "start_date": datetime(2023, 1, 1),
}

MODEL_BUCKET = "model"
DATA_BUCKET = "training-data"
TMP_DIR ='/tmp'

date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
train_data_name = f"label_data/twitter/{date_prefix}/tweets.json"


def download_model(**kwargs):
    """Load the current model from MinIO."""
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

    model_path = f"{TMP_DIR}/current_model"
    os.makedirs(model_path, exist_ok=True)

    objects = client.list_objects(MODEL_BUCKET, prefix="current_model", recursive=True)

    for obj in objects:
        os.makedirs(model_path, exist_ok=True)

        # Download and save model files
        data = client.get_object(MODEL_BUCKET, obj.object_name)
        with open(f"{TMP_DIR}/{obj.object_name}", "wb") as f:
            shutil.copyfileobj(data, f)

    print(f"Model downloaded to {model_path}")

def download_data(**kwargs):
    """Download the labeled data for today from MinIO."""
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    data_path = f"{TMP_DIR}/train_data"
    os.makedirs(data_path, exist_ok=True)

    data = client.get_object(DATA_BUCKET, train_data_name)
    with open(f"{data_path}/tweets.json", "wb") as f:
        shutil.copyfileobj(data, f)

    print(f"Data downloaded to {data_path}/tweets.json")

def retrain_model(**kwargs):
    model_dir = "/tmp/current_model"
    data_path = "/tmp/train_data/tweets.json"
    save_path = "/tmp/output_model"

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)

    with open(data_path, "r") as f:
        raw = json.load(f)
    texts = [x["text"] for x in raw]
    labels = [x["label"] for x in raw]

    label_encoder = LabelEncoder()
    train_labels = label_encoder.fit_transform(labels)
    train_encodings = tokenizer(texts, truncation=True, padding=True)

    train_dataset = Dataset.from_dict({**train_encodings, "label": train_labels})

    args = TrainingArguments(
        output_dir=save_path,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        logging_steps=10,
        logging_dir="./logs"
    )

    trainer = Trainer(model=model, args=args, train_dataset=train_dataset)
    trainer.train()

    print("Model retraining completed. Saving the model...")

    Path(save_path).mkdir(parents=True, exist_ok=True)
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)

    with open(os.path.join(save_path, "label_encoder.pkl"), "wb") as f:
        pickle.dump(label_encoder, f)

    print(f"Model saved to {save_path}")


def upload_model(**kwargs):
    """Upload the retrained model to MinIO with a date prefix."""
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    folder = "/tmp/output_model"
    model_key_prefix = f"checkpoint-{date_prefix}"

    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        with open(file_path, "rb") as f:
            client.put_object(
                MODEL_BUCKET,
                f"{model_key_prefix}/{file}",
                f,
                length=os.path.getsize(file_path),
                content_type="application/octet-stream"
            )


def cleanup_temp_dirs(**kwargs):
    paths = [
        "/tmp/output_model",
        "/tmp/train_data"
    ]

    for path in paths:
        try:
            shutil.rmtree(path)
            print(f"Deleted: {path}")
        except:
            pass


with DAG(
    dag_id="retrain_model",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["retrain", "model"],
) as dag:

    download_model_task = PythonOperator(task_id="download_model", python_callable=download_model)
    download_data_task = PythonOperator(task_id="download_data", python_callable=download_data)
    retrain_model_task = PythonOperator(task_id="retrain_model", python_callable=retrain_model)
    upload_model_task = PythonOperator(task_id="upload_model", python_callable=upload_model)
    cleanup_temp_dirs_task = PythonOperator(task_id="cleanup_temp", python_callable=cleanup_temp_dirs)

    [download_model_task, download_data_task] >> retrain_model_task >> upload_model_task >> cleanup_temp_dirs_task

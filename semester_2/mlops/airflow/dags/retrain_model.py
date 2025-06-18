
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
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MODEL_BUCKET, DATA_BUCKET, TMP_DIR
from utils import download_from_minio
import mlflow
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


default_args = {
    "start_date": datetime(2023, 1, 1),
}

date_prefix = datetime.utcnow().strftime("%Y-%m-%d")


def compute_metrics(pred):
    """Compute metrics."""
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1": f1_score(labels, preds, average="weighted"),
        "precision": precision_score(labels, preds, average="weighted"),
        "recall": recall_score(labels, preds, average="weighted"),
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

def download_data(**kwargs):
    """load the labeled data for today from MinIO."""
    data_path = f"{TMP_DIR}/train_data"
    train_data_name = f"label_data/{date_prefix}/label_train_data.json"

    download_from_minio(
        bucket=DATA_BUCKET,
        prefix_or_key=train_data_name,
        dest_dir=data_path,
        recursive=False
    )

    print(f"Data downloaded to {data_path}/label_train_data.json")

    data_path = f"{TMP_DIR}/validation_data"
    validation_data_name = "validation_data/test.json"

    download_from_minio(
        bucket=DATA_BUCKET,
        prefix_or_key=validation_data_name,
        dest_dir=data_path,
        recursive=False
    )

    print(f"Data downloaded to {data_path}/test.json")

def retrain_model(**kwargs):
    """Retrain the model using the downloaded data."""
    model_dir = "/tmp/current_model"
    data_path = "/tmp/train_data/label_train_data.json"
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
        output_dir="/tmp/training_logs",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        logging_steps=10,
        save_total_limit=1,
        save_strategy="no"
    )

    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("text-classification")

    with mlflow.start_run():
        mlflow.log_param("num_train_epochs", args.num_train_epochs)
        mlflow.log_param("batch_size", args.per_device_train_batch_size)

        trainer = Trainer(
            model=model,
            args=args,
            train_dataset=train_dataset,
            compute_metrics=compute_metrics
        )
        trainer.train()

        preds = trainer.predict(train_dataset).predictions.argmax(axis=1)
        acc = accuracy_score(train_labels, preds)
        mlflow.log_metric("accuracy", acc)

        Path(save_path).mkdir(parents=True, exist_ok=True)
        model.save_pretrained(save_path)
        tokenizer.save_pretrained(save_path)

        with open(os.path.join(save_path, "label_encoder.pkl"), "wb") as f:
            pickle.dump(label_encoder, f)

        mlflow.log_artifact(os.path.join(save_path, "label_encoder.pkl"))

        print(f"Model retrained and logged to MLflow. Accuracy: {acc:.4f}")


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
        "/tmp/train_data",
        "/tmp/validation_data",
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

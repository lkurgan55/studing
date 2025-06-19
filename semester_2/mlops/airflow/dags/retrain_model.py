from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import mlflow
import numpy as np
import os
import json
import shutil
import joblib
from transformers import Trainer, TrainingArguments, AutoModelForSequenceClassification, AutoTokenizer
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from config import DATA_BUCKET, TMP_DIR, MODEL_NAME, MODEL_ALIAS, REGISTER_NAME
from utils import download_from_minio


default_args = {
    "start_date": datetime(2023, 1, 1),
}

date_prefix = datetime.utcnow().strftime("%Y-%m-%d")

def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1": f1_score(labels, preds, average="weighted"),
        "precision": precision_score(labels, preds, average="weighted"),
        "recall": recall_score(labels, preds, average="weighted"),
    }

def download_data(**kwargs):
    """Download training and validation data from MinIO."""
    train_data_path = f"{TMP_DIR}/train_data"
    validation_data_path = f"{TMP_DIR}/validation_data"

    download_from_minio(DATA_BUCKET, f"label_data/{date_prefix}/label_train_data.json", train_data_path)
    download_from_minio(DATA_BUCKET, "validation_data/validation_data.json", validation_data_path)

    print("Data downloaded successfully.")


def retrain_model(**kwargs):
    """Retrain model loaded from MLflow, update metrics and log new version."""
    model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
    local_path = mlflow.artifacts.download_artifacts(artifact_uri=model_uri)

    model_path = os.path.join(local_path, "model")
    tokenizer_path = os.path.join(local_path, "components/tokenizer")
    encoder_path = os.path.join(local_path, "components/encoder", "label_encoder.pkl")

    # Load model, tokenizer, and encoder
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    label_encoder = joblib.load(encoder_path)

    # Load training data
    with open(f"{TMP_DIR}/train_data/label_train_data.json", "r") as f:
        raw = json.load(f)
    texts = [x["text"] for x in raw]
    labels = [x["label"] for x in raw]
    train_labels = [label_encoder[label] for label in labels]

    # Tokenize
    train_encodings = tokenizer(texts, truncation=True, padding=True)
    train_dataset = Dataset.from_dict({**train_encodings, "label": train_labels})

    # MLflow setup
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("antispam-text-classification")

    training_args = TrainingArguments(
        output_dir="/tmp/training_logs",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        logging_steps=10,
        save_strategy="no"
    )

    with mlflow.start_run(run_name=f"retrain_{MODEL_ALIAS}_{date_prefix}"):
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            compute_metrics=compute_metrics,
            tokenizer=tokenizer,
        )
        trainer.train()

        # # Save model + tokenizer + encoder
        output_path = "/tmp/output_model"
        model.save_pretrained(output_path)
        tokenizer.save_pretrained(output_path)
        shutil.copy(encoder_path, os.path.join(output_path, "label_encoder.pkl"))

        # Log to MLflow
        model_info = mlflow.transformers.log_model(
            transformers_model={"model": model, "tokenizer": tokenizer},
            artifact_path="model",
            input_example=texts[0],
            task="text-classification",
            signature=None
        )
        mlflow.log_artifact(os.path.join(output_path, "label_encoder.pkl"), artifact_path="components/encoder")

            # Реєстрація в Model Registry
        mlflow.register_model(
            model_uri=model_info.model_uri,
            name=REGISTER_NAME
        )

        print("✅ Model retrained and logged to MLflow")

def cleanup_temp_dirs(**kwargs):
    paths = [
        f"{TMP_DIR}/output_model",
        f"{TMP_DIR}/train_data",
        f"{TMP_DIR}/validation_data",
        f"{TMP_DIR}/training_logs",
    ]

    for path in paths:
        try:
            shutil.rmtree(path)
            print(f"Deleted: {path}")
        except:
            pass


with DAG(
    dag_id="retrain_model_champion_mlflow",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["retrain", "mlflow"],
) as dag:

    download_data_task = PythonOperator(
        task_id="download_data",
        python_callable=download_data
    )

    retrain_model_task = PythonOperator(
        task_id="retrain_model",
        python_callable=retrain_model
    )

    cleanup_temp_dirs_task = PythonOperator(
        task_id="cleanup_temp",
        python_callable=cleanup_temp_dirs
    )

    download_data_task >> retrain_model_task >> cleanup_temp_dirs_task

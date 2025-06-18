import mlflow
import joblib
from transformers import pipeline
import os

# === Налаштування ===
MODEL_NAME = "text-model"
MODEL_ALIAS = "champion"
MLFLOW_TRACKING_URI = "http://localhost:5000"
ENCODER_PATH = "encoder/label_encoder.pТаkl"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# === Завантажити модель як pipeline-ready об’єкт
model_uri = f"models:/{MODEL_NAME}/{MODEL_ALIAS}"
model_pipeline = mlflow.transformers.load_model(model_uri)

# === Завантажити енкодер як об’єкт (через артефакт)
encoder_path = mlflow.artifacts.download_artifacts(
    model_uri=model_uri,
    artifact_path=ENCODER_PATH
)

label_encoder = joblib.load(encoder_path)

# === Інференс
def predict(text: str) -> dict:
    result = model_pipeline(text)[0]
    label_idx = int(result["label"].replace("LABEL_", ""))
    label = label_encoder.inverse_transform([label_idx])[0]
    return {
        "label": label,
        "score": round(result["score"], 4)
    }

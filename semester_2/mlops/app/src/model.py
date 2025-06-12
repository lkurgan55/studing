from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import joblib
from minio import Minio
import os, shutil

MINIO_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "admin123"
MODEL_BUCKET = "model"
MODEL_PREFIX = "current_model/"
MODEL_DIR = "/tmp/model"
ENCODER_FILE = os.path.join(MODEL_DIR, "label_encoder.pkl")


def download_model_from_minio():
    """Download the model and label encoder from MinIO storage."""
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

    os.makedirs(MODEL_DIR, exist_ok=True)

    objects = client.list_objects(MODEL_BUCKET, prefix=MODEL_PREFIX, recursive=True)
    for obj in objects:
        rel_path = obj.object_name.replace(MODEL_PREFIX, "")
        local_path = os.path.join(MODEL_DIR, rel_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        response = client.get_object(MODEL_BUCKET, obj.object_name)
        with open(local_path, "wb") as f:
            shutil.copyfileobj(response, f)

    client.fget_object(MODEL_BUCKET, "label_encoder.pkl", ENCODER_FILE)

download_model_from_minio()

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
label_encoder = joblib.load(ENCODER_FILE)

classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, device=0)

def predict(text: str) -> dict:
    """Predict the label for the given text using the pre-trained model."""
    result = classifier(text)[0]
    label_idx = int(result["label"].replace("LABEL_", ""))
    label = label_encoder.inverse_transform([label_idx])[0]
    return {
        "label": label,
        "score": round(result["score"], 4)
    }

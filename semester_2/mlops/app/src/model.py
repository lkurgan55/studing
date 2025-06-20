import mlflow
import joblib
import os

MODEL_NAME = "antispam-text-model"
MODEL_ALIAS = "champion"
ENCODER_MLFLOW_PATH = "components/encoder/label_encoder.pkl"

model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"

classifier = mlflow.transformers.load_model(model_uri)
local_path = mlflow.artifacts.download_artifacts(artifact_uri=model_uri)
encoder_path = os.path.join(local_path, ENCODER_MLFLOW_PATH)
label_encoder = joblib.load(encoder_path)

id_to_label = {v: k for k, v in label_encoder.items()}

def predict(text: str) -> dict:
    """Predict the label for a given text using the loaded model."""
    result = classifier(text)[0]
    label_idx = int(result["label"].replace("LABEL_", ""))
    label = id_to_label.get(label_idx, 'other')
    return {
        "label": label,
        "score": round(result["score"], 4)
    }

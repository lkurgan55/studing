import mlflow
import joblib
import os

mlflow.set_tracking_uri("http://localhost:5000")
model_uri = "models:/antispam-text-model@champion"

# Завантажити модель як pipeline
classifier = mlflow.transformers.load_model(model_uri)

# Завантажити всі артефакти моделі в тимчасову папку
local_path = mlflow.artifacts.download_artifacts(artifact_uri=model_uri)

# Тепер просто знайди файл енкодера локально
encoder_path = os.path.join(local_path, "components", "encoder", "label_encoder.pkl")
label_encoder = joblib.load(encoder_path)

id_to_label = {v: k for k, v in label_encoder.items()}

def predict(text: str) -> dict:
    result = classifier(text)[0]
    label_idx = int(result["label"].replace("LABEL_", ""))
    label = id_to_label[label_idx]
    return {
        "label": label,
        "score": round(result["score"], 4)
    }

print(predict("It's spam"))

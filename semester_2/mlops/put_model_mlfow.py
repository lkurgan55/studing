import json
import joblib
import mlflow
import mlflow.transformers
import torch

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from torch.utils.data import DataLoader, TensorDataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# === Налаштування ===
MODEL_PATH = "./model/saved_model"
VAL_PATH = ".train_data/validation_data.json"
ENCODER_PATH = "./model/label_encoder.pkl"
BATCH_SIZE = 128
REGISTER_NAME = "antispam-text-model"

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("antispam-text-classification")

# === Завантаження моделі і токенізатора ===
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

# === Завантаження валідаційного сету ===
with open(VAL_PATH, encoding="utf-8") as f:
    val = json.load(f)

texts = [x["text"] for x in val]
true_labels = [x["label"] for x in val]

# Кодування міток
label_to_id = {label: idx for idx, label in enumerate(sorted(set(true_labels)))}
id_to_label = {v: k for k, v in label_to_id.items()}
labels_ids = [label_to_id[label] for label in true_labels]

# Збереження енкодера
joblib.dump(label_to_id, ENCODER_PATH)

# === Токенізація ===
encodings = tokenizer(
    texts,
    truncation=True,
    padding=True,
    max_length=512,
    return_tensors="pt"
)

# === DataLoader ===
dataset = TensorDataset(encodings['input_ids'], encodings['attention_mask'], torch.tensor(labels_ids))
loader = DataLoader(dataset, batch_size=BATCH_SIZE)

# === Прогін моделі ===
all_preds = []
all_labels = []
with torch.no_grad():
    for input_ids, attention_mask, labels in loader:
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        preds = outputs.logits.argmax(dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.cpu().numpy())

# === Метрики ===
accuracy = accuracy_score(all_labels, all_preds)
f1 = f1_score(all_labels, all_preds, average="weighted")
precision = precision_score(all_labels, all_preds, average="weighted")
recall = recall_score(all_labels, all_preds, average="weighted")

print(f"Accuracy:  {accuracy:.4f}")
print(f"F1 Score:  {f1:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")

# === Логування в MLflow ===
with mlflow.start_run(run_name="upload-start-model") as run:
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1", f1)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)

    # Логування енкодера
    mlflow.log_artifact(ENCODER_PATH, artifact_path="model/components/encoder")

    # Логування моделі
    model_info = mlflow.transformers.log_model(
        transformers_model={"model": model, "tokenizer": tokenizer},
        artifact_path="model",
        task="text-classification"
    )

    # Реєстрація в Model Registry
    mlflow.register_model(
        model_uri=model_info.model_uri,
        name=REGISTER_NAME
    )

print("✅ Модель, метрики і енкодер зареєстровані в MLflow.")

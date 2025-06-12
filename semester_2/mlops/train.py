import json
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from datasets import Dataset
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, TrainingArguments, Trainer
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import pickle

# Load and prepare datasets
with open("train_data/train.json", "r", encoding="utf-8") as f:
    train_data = json.load(f)

with open("train_data/test.json", "r", encoding="utf-8") as f:
    test_data = json.load(f)

train_df = pd.DataFrame(train_data)
test_df = pd.DataFrame(test_data)

# Label encoding
label_encoder = LabelEncoder()
train_df["label_id"] = label_encoder.fit_transform(train_df["label"]) # Fit on training data
test_df["label_id"] = label_encoder.transform(test_df["label"])

# Tokenization
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
train_encodings = tokenizer(train_df["text"].tolist(), truncation=True, padding=True)
test_encodings = tokenizer(test_df["text"].tolist(), truncation=True, padding=True)

# Prepare Hugging Face datasets
train_dataset = Dataset.from_dict({**train_encodings, "label": train_df["label_id"].tolist()})
val_dataset = Dataset.from_dict({**test_encodings, "label": test_df["label_id"].tolist()})

# Load model
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased", num_labels=len(label_encoder.classes_)
)

# Metric function
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

# Training arguments
training_args = TrainingArguments(
    output_dir="./model",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    eval_strategy="no"
)

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    tokenizer=tokenizer
)

# Train model
trainer.train()

# Save label encoder
with open("model/label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

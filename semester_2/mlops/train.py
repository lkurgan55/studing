# train.py

from datasets import load_dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
import torch

# 1. Завантажуємо невеликий набір з imdb (можна буде замінити на власний)
dataset = load_dataset("imdb", split="train[:2%]")  # ~500 записів
dataset = dataset.train_test_split(test_size=0.2)

# 2. Токенізуємо
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

def tokenize(example):
    return tokenizer(example["text"], truncation=True, padding="max_length")

tokenized_dataset = dataset.map(tokenize, batched=True)

# 3. Створюємо модель
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)

# 4. Параметри тренування
training_args = TrainingArguments(
    output_dir="./model/saved_model",
    num_train_epochs=2,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    logging_steps=10,
)

# 5. Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
)

# 6. Тренування
trainer.train()

# 7. Збереження моделі і токенайзера
model.save_pretrained("./model/saved_model")
tokenizer.save_pretrained("./model/saved_model")

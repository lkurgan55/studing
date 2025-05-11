from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "./model/saved_model"

# Завантажуємо токенайзер і модель
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

# Створюємо pipeline для класифікації тексту
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

def predict(text: str) -> dict:
    """
    Прогноз для одного тексту.
    Повертає label та score (ймовірність).
    """
    result = classifier(text)[0]
    return {
        "label": result["label"],
        "score": round(result["score"], 4)
    }

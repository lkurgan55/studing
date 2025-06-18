import json
import re
import string

VAL_FILE = "test.json"
OUT_FILE = "validation_data.json"

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    allowed = string.ascii_letters + string.digits + string.punctuation + " "
    return ''.join(c for c in text if c in allowed)

# 1. Завантаження
with open(VAL_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. Очищення
for entry in data:
    entry["text"] = clean_text(entry["text"])

# 3. Збереження
with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Cleaned validation set saved to {OUT_FILE}")

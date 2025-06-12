import json
import random

with open("merged_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

random.shuffle(data)

split_index = int(len(data) * 0.7)
train_data = data[:split_index]
test_data = data[split_index:]

with open("train.json", "w", encoding="utf-8") as f:
    json.dump(train_data, f, indent=2, ensure_ascii=False)

with open("test.json", "w", encoding="utf-8") as f:
    json.dump(test_data, f, indent=2, ensure_ascii=False)

print(f"Distrubition: {len(train_data)} training, {len(test_data)} testing.")

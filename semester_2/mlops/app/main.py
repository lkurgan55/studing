from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()
classifier = pipeline("text-classification", model="./model/saved_model")

class TextInput(BaseModel):
    text: str

@app.post("/analyze-post")
def analyze_post(data: TextInput):
    result = classifier(data.text)
    return {"label": result[0]["label"], "score": round(result[0]["score"], 2)}

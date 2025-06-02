from fastapi import FastAPI
from pydantic import BaseModel
from model import predict

app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.post("/analyze-post")
def analyze_post(data: TextInput) -> dict[str, str]:
    """Endpoint to analyze the text input and return the predicted label and score."""
    return predict(data.text)

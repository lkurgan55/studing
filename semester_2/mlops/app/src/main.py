from fastapi import FastAPI
from pydantic import BaseModel
from model import predict
import redis
import json

app = FastAPI()
r = redis.from_url("redis://redis:6379")


class TextInput(BaseModel):
    text: str


class PredictionResponse(BaseModel):
    label: str
    score: float


@app.post("/analyze-post")
def analyze_post(data: TextInput) -> PredictionResponse:
    """Endpoint to analyze the text input and return the predicted label and score."""
    result = predict(data.text)
    return PredictionResponse(label=result["label"], score=result["score"])

@app.get("/top-posts")
def get_top_posts():
    """Endpoint to retrieve the top posts from Redis."""
    data = r.get("top_posts")
    if not data:
        return []
    return json.loads(data)

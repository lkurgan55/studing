from fastapi import FastAPI
from pydantic import BaseModel
from model import predict
import redis
import json

app = FastAPI()
r = redis.from_url("redis://redis:6379")

class TextInput(BaseModel):
    text: str

@app.post("/analyze-post")
def analyze_post(data: TextInput) -> dict[str, str]:
    """Endpoint to analyze the text input and return the predicted label and score."""
    return predict(data.text)

@app.get("/top-posts")
def get_top_posts():
    data = r.get("top_posts")
    if not data:
        return {"posts": []}
    posts = json.loads(data)
    return {"posts": posts}

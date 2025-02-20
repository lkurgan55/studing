import uvicorn
from fastapi import FastAPI


app = FastAPI()

@app.get("/")
async def root():
   return "Hello World"

if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=80, log_level="info", reload=True)

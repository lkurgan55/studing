from fastapi import FastAPI
from fastapi.responses import RedirectResponse

import uvicorn
import os


myhost = os.uname()[1]
app = FastAPI()

@app.get("/")
def read_root():
   return RedirectResponse(url='/docs')

@app.get("/calculate")
def get_records(expression: str = '5+5/5-3'):
   print(f"calculating {expression}")
   return {
      "host": myhost,
      "result": eval(expression)
   }

if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=81, log_level="info", reload=True)

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

import uvicorn
import os
import aiohttp


myhost = os.uname()[1]
app = FastAPI()

@app.get("/")
def read_root():
   return RedirectResponse(url='/docs')

@app.get("/calculate")
async def calculate(expression: str = '5+5/5-3'):
   async with aiohttp.ClientSession() as session:
        async with session.get(f'http://nginx:8080/calculate', params={'expression': expression}) as resp:
            return await resp.json()

if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=80, log_level="info", reload=True)

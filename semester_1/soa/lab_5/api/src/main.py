from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import RedirectResponse

import uvicorn
import os

from redis_limiter import Limiter
from queue_limiter import QueueLimiter

from starlette.concurrency import run_in_threadpool


myhost = os.uname()[1]
app = FastAPI()

app.limiter = Limiter()
app.queue_limiter = QueueLimiter(4)
app.request_id = 0

@app.get("/")
async def read_root():
   return RedirectResponse(url='/docs')

@app.get("/calculate")
async def calculate(request: Request, expression: str = '5+5/5-3'):
   clientIp = request.client.host
   if await app.limiter.limiter(clientIp, 12): # 12 - limit of requests, can be diffirent for users
      request = {
         'id': app.request_id,
         'params': {'expression': expression}
      }
      app.request_id += 1
      return await run_in_threadpool(app.queue_limiter.make_request, request)
      
   else:
      raise HTTPException(status_code=429, detail="Too many requests")

if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=80, log_level="info", workers=1)

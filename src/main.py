import json
from datetime import datetime, date

import uvicorn
from fastapi.responses import RedirectResponse
from fastapi import Depends, FastAPI, APIRouter

from schema.record import Record, UpdateRecord
from handlers.db import DB


crud_endpoints = APIRouter()
app = FastAPI()

@crud_endpoints.get("/get_records")
def get_records(record_id: str = 'all'): 
   return app.db.get_record(record_id)

@crud_endpoints.delete("/del_records")
def del_records(record_id: str = 'all'):
   return app.db.del_record(record_id)

@crud_endpoints.put("/add_record")
def add_record(record: Record = Depends()):
   return app.db.add_record(record.dict())

@crud_endpoints.put("/update_record")
def update_record(record_id: str, record: UpdateRecord = Depends()):
   return app.db.update_record(record_id, record.dict())

app.include_router(crud_endpoints, prefix="/crud", tags=['crud_endpoints'])

@app.on_event('startup')
def startup():
   app.db = DB('db.json')

@app.on_event('shutdown')
def shutdown():
   pass

@app.get("/")
def read_root():
   return RedirectResponse(url='/docs')


if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=80, log_level="info", reload=True)

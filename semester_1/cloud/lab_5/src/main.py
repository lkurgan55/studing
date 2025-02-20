import configparser

import uvicorn
from fastapi.responses import RedirectResponse
from fastapi import Depends, FastAPI, APIRouter

from schema.record import Record, UpdateRecord, Category
from handlers.db import DB


crud_endpoints = APIRouter()
endpoints = APIRouter()
app = FastAPI()

@crud_endpoints.get("/get_records")
def get_records(record_id: int = None): 
   return app.db.get_record(record_id)

@crud_endpoints.delete("/del_records")
def del_records(record_id: int = None):
   return app.db.del_record(record_id)

@crud_endpoints.post("/add_record")
def add_record(record: Record = Depends()):
   return app.db.add_record(record.dict())

@crud_endpoints.put("/update_record")
def update_record(record_id: int, record: UpdateRecord = Depends()):
   return app.db.update_record(record_id, record.dict())

@endpoints.get("/get_total_by_category")
def get_total_by_category(category: Category = None): 
   return app.db.get_total_by_category(category.value if category else None)

app.include_router(crud_endpoints, prefix="/crud", tags=['crud_endpoints'])
app.include_router(endpoints, prefix="/endpoints", tags=['endpoints'])

@app.on_event('startup')
def startup():
   config = configparser.ConfigParser()
   config.read('/studing/config.ini')
   app.db = DB(
      config['DB']['db_url']
   )

@app.on_event('shutdown')
def shutdown():
   app.db.shutdown()

@app.get("/")
def read_root():
   return RedirectResponse(url='/docs')


if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=80, log_level="info", reload=True)

from pydantic import BaseModel, validator
from pydantic.types import PositiveInt
from autoname import AutoName
from enum import auto


class Category(AutoName):
    food = auto()
    games = auto()
    car = auto()
    bills = auto()

class Record(BaseModel):
    name: str
    category: Category
    amout: float
    descriptiom: str | None = None
    
    @validator("category")
    def get_value(cls, value):
        if value:
            return value.value

class UpdateRecord(BaseModel):
    name: str | None = None
    category: Category | None = None
    amout: float | None = None
    descriptiom: str | None = None
    
    @validator("category")
    def get_value(cls, value):
        if value:
            return value.value

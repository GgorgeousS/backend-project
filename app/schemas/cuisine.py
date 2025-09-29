from pydantic import BaseModel, Field
from typing import Optional

class CuisineBase(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Название кухни"
    )

class CuisineCreate(CuisineBase):
    pass

class CuisineUpdate(BaseModel):
    name: Optional[str] = None

class CuisineRead(CuisineBase):
    id: int

    class Config:
        orm_mode = True

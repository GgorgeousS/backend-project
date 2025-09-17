from pydantic import BaseModel
from typing import Optional


class RecipeBase(BaseModel):
    title: str
    description: str
    cooking_time: int
    difficulty: int


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cooking_time: Optional[int] = None
    difficulty: Optional[int] = None


class RecipeRead(RecipeBase):
    id: int

    class Config:
        orm_mode = True
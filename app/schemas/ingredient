from pydantic import BaseModel, Field
from typing import Optional

class IngredientBase(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Название ингредиента"
    )

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(BaseModel):
    name: Optional[str] = None

class IngredientRead(IngredientBase):
    id: int

    class Config:
        orm_mode = True

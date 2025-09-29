from pydantic import BaseModel, Field
from typing import Optional


class RecipeBase(BaseModel):
    title: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=200,
        description="Название рецепта"
    )
    description: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=2000,
        description="Описание рецепта"
    )
    cooking_time: Optional[int] = Field(
        None, 
        ge=1, 
        le=1440,
        description="Время приготовления в минутах"
    )
    difficulty: Optional[int] = Field(
        None, 
        ge=1, 
        le=10,
        description="Сложность от 1 до 10"
    )



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

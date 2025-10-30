from pydantic import BaseModel, Field
from typing import List, Optional
from .cuisine import CuisineRead
from .allergen import AllergenRead
from .recipe_ingredient import RecipeIngredientCreate, RecipeIngredientRead


class RecipeBase(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    cooking_time: Optional[int] = Field(None, ge=1, le=1440)
    difficulty: Optional[int] = Field(None, ge=1, le=10)

class RecipeCreate(RecipeBase):
    cuisine_id: int
    allergens: List[int]
    ingredients: List[RecipeIngredientCreate]

class RecipeRead(RecipeBase):
    id: int
    cuisine: CuisineRead
    allergens: List[AllergenRead]
    recipe_ingredients: List[RecipeIngredientRead]
    class Config:
        from_attributes = True
        

class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cooking_time: Optional[int] = None
    difficulty: Optional[int] = None

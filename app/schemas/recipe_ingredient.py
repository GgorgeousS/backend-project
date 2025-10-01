from pydantic import BaseModel

class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: int
    measurement: int

class RecipeIngredientRead(BaseModel):
    id: int
    ingredient_id: int
    quantity: int
    measurement: int
    class Config:
        from_attributes = True

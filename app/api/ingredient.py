from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from typing import List
from .dependencies import SessionDep

from models.recipe import Ingredient
from schemas.ingredient import IngredientCreate, IngredientRead, IngredientUpdate

router = APIRouter(
    prefix="/ingredients",
    tags=["ingredients"],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=IngredientRead)
async def create_ingredient(ingredient: IngredientCreate, session: SessionDep):
    db_ingredient = Ingredient(**ingredient.model_dump())
    session.add(db_ingredient)
    await session.commit()
    await session.refresh(db_ingredient)
    return db_ingredient

@router.get("/", response_model=List[IngredientRead])
async def read_ingredients(session: SessionDep):
    stmt = select(Ingredient).order_by(Ingredient.id)
    ingredients = await session.scalars(stmt)
    return ingredients.all()

@router.get("/{ingredient_id}", response_model=IngredientRead)
async def read_ingredient(ingredient_id: int, session: SessionDep):
    ingredient = await session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient

@router.put("/{ingredient_id}", response_model=IngredientRead)
async def update_ingredient(ingredient_id: int, ingredient_update: IngredientUpdate, session: SessionDep):
    ingredient = await session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    for key, value in ingredient_update.model_dump(exclude_unset=True).items():
        setattr(ingredient, key, value)
    await session.commit()
    await session.refresh(ingredient)
    return ingredient

@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingredient(ingredient_id: int, session: SessionDep):
    ingredient = await session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    await session.delete(ingredient)
    await session.commit()

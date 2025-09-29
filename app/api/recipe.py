from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from typing import List
from .dependencies import SessionDep

from models.recipe import Recipe
from schemas.recipe import RecipeCreate, RecipeRead, RecipeUpdate

#создание роутера
router = APIRouter(
    prefix="/recipes",
    tags=["recipes"], 
)

#создание рецепта
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RecipeRead)
async def create_recipe(recipe: RecipeCreate, session : SessionDep):
    db_recipe = Recipe(**recipe.model_dump())
    session.add(db_recipe)
    await session.commit()
    await session.refresh(db_recipe)
    return db_recipe

#получение всех рецептов
@router.get("/", response_model=List[RecipeRead])
async def read_recipes(session : SessionDep):
    stmt = select(Recipe).order_by(Recipe.id)
    recipes = await session.scalars(stmt)
    return recipes.all()

#получение одного рецепта по id
@router.get("/{recipe_id}", response_model=RecipeRead)
async def read_recipe(recipe_id: int, session : SessionDep):
    recipe = await session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

#обновление рецепта
@router.put("/{recipe_id}", response_model=RecipeRead)
async def update_recipe(recipe_id: int, recipe_update: RecipeUpdate, session : SessionDep):
    recipe = await session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    for key, value in recipe_update.model_dump(exclude_unset=True).items():
        setattr(recipe, key, value)
    await session.commit()
    session.refresh(recipe)
    return recipe

#удаление рецепта
@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(recipe_id: int, session : SessionDep):
    recipe = await session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    await session.delete(recipe)
    await session.commit()

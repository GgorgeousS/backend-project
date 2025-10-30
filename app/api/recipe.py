from fastapi import APIRouter, status, HTTPException
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import selectinload

from .dependencies import SessionDep
from models.recipe import Recipe, Cuisine, Allergen, Ingredient, RecipeIngredient, recipe_allergens
from schemas.recipe import RecipeCreate, RecipeRead
from config.config import settings

router = APIRouter(
    tags=["Recipes"],
    prefix=settings.url.recipes,
)


@router.get("", response_model=list[RecipeRead])
async def get_recipes(
    session: SessionDep,
) -> list[RecipeRead]:
    """Получение всех рецептов"""
    stmt = (
        select(Recipe)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.recipe_ingredients).selectinload(
                RecipeIngredient.ingredient
            ),
        )
        .order_by(Recipe.id)
    )

    result = await session.execute(stmt)
    recipes = result.scalars().all()

    if not recipes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipes not found"
        )
    
    return recipes


@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
async def create_recipes(
    session: SessionDep,
    recipe_data: RecipeCreate,
) -> RecipeRead:
    """Создание нового рецепта"""
    # Проверка существования кухни
    cuisine = await session.get(Cuisine, recipe_data.cuisine_id)
    if not cuisine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cuisine with id {recipe_data.cuisine_id} not found",
        )

    # Проверка и загрузка аллергенов
    allergens = []
    if recipe_data.allergens:
        stmt = select(Allergen).where(Allergen.id.in_(recipe_data.allergens))
        result = await session.execute(stmt)
        allergens = result.scalars().all()

        if len(allergens) != len(recipe_data.allergens):
            found_ids = {a.id for a in allergens}
            missing_ids = set(recipe_data.allergens) - found_ids
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Allergens with ids {missing_ids} not found",
            )

    # Проверка существования ингредиентов
    ingredient_ids = [ing.ingredient_id for ing in recipe_data.ingredients]
    ingredients_map = {}
    if ingredient_ids:
        stmt = select(Ingredient).where(Ingredient.id.in_(ingredient_ids))
        result = await session.execute(stmt)
        ingredients = result.scalars().all()

        if len(ingredients) != len(ingredient_ids):
            found_ids = {i.id for i in ingredients}
            missing_ids = set(ingredient_ids) - found_ids
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredients with ids {missing_ids} not found",
            )
        
        # Создаем словарь для быстрого доступа к ингредиентам
        ingredients_map = {ing.id: ing for ing in ingredients}

    # Создаем объект Recipe с основными данными
    recipe_data_dict = recipe_data.model_dump(
        exclude={"allergens", "ingredients", "cuisine_id"}
    )
    
    # Создаем объект Recipe со всеми связями
    recipe = Recipe(
        **recipe_data_dict,
        cuisine=cuisine,  # устанавливаем связь с кухней через объект
        allergens=allergens,  # устанавливаем связь с аллергенами
        recipe_ingredients=[
            RecipeIngredient(
                ingredient=ingredients_map[ing_data.ingredient_id],  # устанавливаем связь с ингредиентом
                quantity=ing_data.quantity,
                measurement=ing_data.measurement,
            )
            for ing_data in recipe_data.ingredients
        ]
    )
    
    session.add(recipe)

    try:
        await session.commit()
        
        # Загружаем рецепт со всеми связями
        stmt = (
            select(Recipe)
            .where(Recipe.id == recipe.id)
            .options(
                selectinload(Recipe.cuisine),
                selectinload(Recipe.allergens),
                selectinload(Recipe.recipe_ingredients).selectinload(
                    RecipeIngredient.ingredient
                ),
            )
        )
        result = await session.execute(stmt)
        recipe = result.scalar_one()

        return recipe

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating recipe: {str(e)}",
        )


@router.get("/{id}", response_model=RecipeRead)
async def get_recipe(
    session: SessionDep,
    id: int,
) -> RecipeRead:
    """Получение рецепта по его id"""
    stmt = (
        select(Recipe)
        .where(Recipe.id == id)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.recipe_ingredients).selectinload(
                RecipeIngredient.ingredient
            ),
        )
    )

    result = await session.execute(stmt)
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {id} not found",
        )
    
    return recipe


@router.put("/{id}", response_model=RecipeRead)
async def update_recipe(
    session: SessionDep,
    id: int,
    recipe_update: RecipeCreate,
) -> RecipeRead:
    """Обновление рецепта по его id"""
    recipe = await session.get(Recipe, id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {id} not found",
        )

    # Проверка существования кухни
    if recipe_update.cuisine_id:
        cuisine = await session.get(Cuisine, recipe_update.cuisine_id)
        if not cuisine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cuisine with id {recipe_update.cuisine_id} not found",
            )

    # Проверка и загрузка аллергенов
    allergens = []
    if recipe_update.allergens:
        stmt = select(Allergen).where(
            Allergen.id.in_(recipe_update.allergens)
        )
        result = await session.execute(stmt)
        allergens = result.scalars().all()

        if len(allergens) != len(recipe_update.allergens):
            found_ids = {a.id for a in allergens}
            missing_ids = set(recipe_update.allergens) - found_ids
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Allergens with ids {missing_ids} not found",
            )

    # Проверка существования ингредиентов
    ingredient_ids = [ing.ingredient_id for ing in recipe_update.ingredients]
    if ingredient_ids:
        stmt = select(Ingredient).where(Ingredient.id.in_(ingredient_ids))
        result = await session.execute(stmt)
        ingredients = result.scalars().all()

        if len(ingredients) != len(ingredient_ids):
            found_ids = {i.id for i in ingredients}
            missing_ids = set(ingredient_ids) - found_ids
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredients with ids {missing_ids} not found",
            )

    # Обновление основных полей рецепта
    update_data = recipe_update.model_dump(
        exclude={"allergens", "ingredients"}, exclude_unset=True
    )
    for field, value in update_data.items():
        setattr(recipe, field, value)

    # Обновление связей с аллергенами
    if recipe_update.allergens is not None:
        recipe.allergens = allergens

    # Обновление связей с ингредиентами
    if recipe_update.ingredients is not None:
        # Удаляем старые связи с ингредиентами
        for recipe_ingredient in recipe.recipe_ingredients:
            await session.delete(recipe_ingredient)
        
        # Создаем новые связи с ингредиентами
        ingredients_map = {ing.id: ing for ing in ingredients}
        for ingredient_data in recipe_update.ingredients:
            recipe_ingredient = RecipeIngredient(
                recipe_id=id,
                ingredient_id=ingredient_data.ingredient_id,
                quantity=ingredient_data.quantity,
                measurement=ingredient_data.measurement,
            )
            session.add(recipe_ingredient)

    try:
        await session.commit()

        # Загружаем обновленный рецепт со всеми связями
        stmt = (
            select(Recipe)
            .where(Recipe.id == id)
            .options(
                selectinload(Recipe.cuisine),
                selectinload(Recipe.allergens),
                selectinload(Recipe.recipe_ingredients).selectinload(
                    RecipeIngredient.ingredient
                ),
            )
        )
        result = await session.execute(stmt)
        recipe = result.scalar_one()

        return recipe

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating recipe: {str(e)}",
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    session: SessionDep,
    id: int,
) -> None:
    """Удаление рецепта по его id"""
    recipe = await session.get(Recipe, id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {id} not found",
        )

    await session.delete(recipe)
    await session.commit()

import uvicorn
from fastapi import FastAPI, Query, Path, Body, Form, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from config import settings
from contextlib import asynccontextmanager
from typing import Optional, List
import os
import uuid
from pathlib import Path as PathLib

from models import db_helper, Base, Recipe, RecipeCreate, RecipeUpdate, RecipeResponse
from models import Item, User, ItemWithOwner, UserForm, RecipeTemp
from api import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Создаем директорию для загрузок при старте
    os.makedirs("static/uploads", exist_ok=True)

    yield
    # shutdown
    await db_helper.dispose()

main_app = FastAPI(lifespan=lifespan)
main_app.mount("/static", StaticFiles(directory="static"), name="static")
main_app.include_router(api_router)

# In-memory storage для тестовых рецептов
recipes_temp_db = {}

# ===== ЧАСТЬ A: Реализация маршрута /test =====

# 1. Примеры из документации FastAPI
@main_app.post("/test/items/")
async def test_create_item(item: Item):
    return item

@main_app.get("/test/items/")
async def test_read_items(
    q: Optional[str] = Query(None, min_length=3, max_length=50),
    skip: int = 0,
    limit: int = 100
):
    results = {"items": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]}
    if q:
        results.update({"q": q})
    return results

@main_app.get("/test/items/{item_id}")
async def test_read_item(
    item_id: int = Path(..., gt=0, description="The ID of the item"),
    q: Optional[str] = None
):
    return {"item_id": item_id, "q": q}

@main_app.get("/test/users/")
async def test_read_users(
    active: bool = True,
    admin: bool = False
):
    return {"active": active, "admin": admin}

@main_app.post("/test/items-with-owner/")
async def test_create_item_with_owner(item_with_owner: ItemWithOwner):
    return item_with_owner

@main_app.post("/test/login/")
async def test_login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}

@main_app.post("/test/login-model/")
async def test_login_model(user_form: UserForm = Form(...)):
    return {"username": user_form.username}

# 2. Обработка query-параметра format
@main_app.get("/test/")
async def test_format(format: str = Query("json", regex="^(json|html)$")):
    data = {
        "message": "Hello World",
        "status": "success",
        "data": {"id": 1, "name": "Test Item"}
    }
    
    if format == "html":
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>{data['message']}</h1>
            <p>Status: {data['status']}</p>
            <p>ID: {data['data']['id']}</p>
            <p>Name: {data['data']['name']}</p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    else:
        return data

# 3. Загрузка изображений
@main_app.post("/test/upload-image/")
async def test_upload_image(file: UploadFile = File(...)):
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
    file_extension = PathLib(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail="Only PNG, JPG, and WEBP formats are allowed"
        )
    
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = f"static/uploads/{unique_filename}"
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return {"url": f"/static/uploads/{unique_filename}"}

# ===== ЧАСТЬ B: CRUD-операции для тестовых рецептов =====
@main_app.post("/test/recipes/", response_model=RecipeTemp)
async def test_create_recipe(recipe: RecipeTemp):
    recipe_id = str(uuid.uuid4())
    recipes_temp_db[recipe_id] = recipe.dict()
    return {**recipes_temp_db[recipe_id], "id": recipe_id}

@main_app.get("/test/recipes/", response_model=List[RecipeTemp])
async def test_read_recipes():
    return [{"id": k, **v} for k, v in recipes_temp_db.items()]

@main_app.get("/test/recipes/{recipe_id}", response_model=RecipeTemp)
async def test_read_recipe(recipe_id: str):
    if recipe_id not in recipes_temp_db:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {**recipes_temp_db[recipe_id], "id": recipe_id}

@main_app.put("/test/recipes/{recipe_id}", response_model=RecipeTemp)
async def test_update_recipe(recipe_id: str, recipe: RecipeTemp):
    if recipe_id not in recipes_temp_db:
        raise HTTPException(status_code=404, detail="Recipe not found")
    recipes_temp_db[recipe_id] = recipe.dict()
    return {**recipes_temp_db[recipe_id], "id": recipe_id}

@main_app.delete("/test/recipes/{recipe_id}")
async def test_delete_recipe(recipe_id: str):
    if recipe_id not in recipes_temp_db:
        raise HTTPException(status_code=404, detail="Recipe not found")
    del recipes_temp_db[recipe_id]
    return {"message": "Recipe deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )

from fastapi.responses import HTMLResponse
from config import settings
from fastapi import APIRouter, FastAPI, Path, Query, Body, Form, File, UploadFile, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
import os
import uuid
from pathlib import Path as PathLib
router = APIRouter(
    tags=["Test"],
    prefix=settings.url.test,
)
UPLOAD_DIR = PathLib("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)



from fastapi import FastAPI
from pydantic import BaseModel


# Body - Пример 1 
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


@router.post("")
async def create_item(item: Item):
    return {"item": item, "message": "Элемент успешно создан"}

# Query Parameters and String Validations - Пример 2 - Параметры запроса query
@router.get("")
async def read_items(
    q: Optional[str] = Query(
        None, 
        min_length=3, 
        max_length=50, 
        description="Строка запроса для поиска"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000)
):
    return {"q": q, "skip": skip, "limit": limit}

# Path Parameters and Numeric Validations - Пример 3 - path параметры
@router.get("/{item_id}")
async def read_item_path(
    item_id: int = Path(..., gt=0, description="Идентификатор элемента"),
    q: Optional[str] = Query(None)
):
    return {"item_id": item_id, "q": q}

# Query Parameter Models - Пример 4 - модель как query параметр
class FilterParams(BaseModel):
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

@router.get("/models/")
async def read_items_models(filter_params: FilterParams = Query(...)):
    return {"filters": filter_params}

# Nested Models - Пример 5 - получаем поля формы вместо json (вложенная модель)
class Image(BaseModel):
    url: str
    name: str

class NewItem(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    tags: List[str] = []
    image: Optional[Image] = None

@router.post("/nested_models/")
async def create_item_model(item: NewItem):
    return {"item": item}

# Request Forms - Пример 6 - поля формы
@router.post("/login/")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    return {"username": username, "password": "*****"}

# Request Form Models - Пример 7 - модели pydantic для полей формы
class User(BaseModel):
    username: str
    password: str

@router.post("/register/")
async def register(user: User = Form(...)):
    return {"user": user, "message": "Регистрация прошла успешно"}



@router.get("/test/format/")
async def format_example(format: str = Query("json", regex="^(json|html)$")):
    data = {
        "name": "Example Data",
        "value": 42,
        "items": ["item1", "item2", "item3"],
        "timestamp": datetime.now().isoformat()
    }
    
    if format == "html":
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Example HTML</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .item {{ padding: 10px; border-bottom: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{data['name']}</h1>
                <p>Value: {data['value']}</p>
                <p>Timestamp: {data['timestamp']}</p>
                <h2>Items:</h2>
                <ul>
                    {"".join(f'<li class="item">{item}</li>' for item in data['items'])}
                </ul>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    return data

@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    
    # Генерируем уникальное имя файла
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Сохраняем файл
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    finally:
        await file.seek(0)
    
    # Возвращаем URL к файлу
    image_url = f"/static/uploads/{unique_filename}"
    return {
        "message": "File uploaded successfully",
        "filename": unique_filename,
        "url": image_url,
        "content_type": file.content_type
    }

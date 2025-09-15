from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Text, Integer, CheckConstraint, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

from .base import Base

# SQLAlchemy модель (оригинальная)
class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "difficulty >= 1 AND difficulty <= 5", name="check_difficulty_range"
        ),
    )

    def __repr__(self):
        return f"Recipe(id={self.id}, title={self.title})"

# Pydantic модели для API
class RecipeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str
    cooking_time: int = Field(..., gt=0)
    difficulty: int = Field(..., ge=1, le=5)

    @validator('difficulty')
    def validate_difficulty(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Difficulty must be between 1 and 5')
        return v

class RecipeCreate(RecipeBase):
    pass

class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    cooking_time: Optional[int] = Field(None, gt=0)
    difficulty: Optional[int] = Field(None, ge=1, le=5)

class RecipeResponse(RecipeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Модели для части A задания
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class ItemWithOwner(BaseModel):
    item: Item
    owner: User

class UserForm(BaseModel):
    username: str
    password: str

# Модель для временного хранения рецептов (in-memory)
class RecipeTemp(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    ingredients: List[str] = Field(..., min_items=1)
    instructions: str
    cooking_time: int = Field(..., gt=0)
    difficulty: str = Field(..., regex="^(easy|medium|hard)$")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Spaghetti Carbonara",
                "description": "Classic Italian pasta dish",
                "ingredients": ["spaghetti", "eggs", "pecorino cheese", "guanciale", "black pepper"],
                "instructions": "Cook pasta, mix with other ingredients...",
                "cooking_time": 20,
                "difficulty": "medium"
            }
        }

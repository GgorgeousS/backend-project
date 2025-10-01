from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, CheckConstraint, ForeignKey, Table
from enum import IntEnum
from sqlalchemy import Column, Integer, ForeignKey, Table

from .base import Base

class MeasurementEnum(IntEnum):
    GRAMS = 1
    PIECES = 2
    MILLILITERS = 3

    @property
    def label(self) -> str:
        return {
            MeasurementEnum.GRAMS: "г",
            MeasurementEnum.PIECES: "шт",
            MeasurementEnum.MILLILITERS: "мл",
        }[self]

class Cuisine(Base):
    __tablename__ = "cuisines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    recipes = relationship("Recipe", back_populates="cuisine")

class Allergen(Base):
    __tablename__ = "allergens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    recipes = relationship(
        "Recipe",
        secondary="recipe_allergens",
        back_populates="allergens"
    )

class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    recipe_ingredients = relationship("RecipeIngredient", back_populates="ingredient")

# --- Связующая таблица Рецепты-Аллергены ---
recipe_allergens = Table(
    "recipe_allergens",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("allergen_id", Integer, ForeignKey("allergens.id"), primary_key=True)
)

# --- Таблица Рецепты-Ингредиенты ---
class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id"))
    ingredient_id: Mapped[int] = mapped_column(Integer, ForeignKey("ingredients.id"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    measurement: Mapped[int] = mapped_column(Integer, nullable=False)  # Используйте MeasurementEnum в коде

    recipe = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")

# --- Доработанная модель Recipe ---
class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    cuisine_id: Mapped[int] = mapped_column(Integer, ForeignKey("cuisines.id"))

    cuisine = relationship("Cuisine")
    allergens: Mapped[list["Allergen"]] = relationship(
        "Allergen", secondary="recipe_allergens", back_populates="recipes"
    )
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Recipe(id={self.id}, title={self.title})"


#class Recipe(Base):
#    __tablename__ = "recipes"
#
#    id: Mapped[int] = mapped_column(primary_key=True)
#    title: Mapped[str] = mapped_column(String(255))
#    description: Mapped[str] = mapped_column(Text)
#    cooking_time: Mapped[int] = mapped_column(Integer)
#    difficulty: Mapped[int] = mapped_column(Integer, default=1)
#
#    # __table_args__ = (
#    #     CheckConstraint(
#    #         "difficulty >= 1 AND difficulty <= 5", name="check_difficulty_range"
#    #     ),
#    # )
#
#    def __repr__(self):
#        return f"Recipe(id={self.id}, title={self.title})"
#

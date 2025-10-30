from enum import IntEnum
from pydantic import BaseModel, ConfigDict, field_serializer
from .ingredient import IngredientRead

class MeasurementEnum(IntEnum):
    GRAMS = 1
    PIECES = 2
    MILLILITERS = 3

    def __str__(self) -> str:
        return {
            MeasurementEnum.GRAMS: "г",
            MeasurementEnum.PIECES: "шт",
            MeasurementEnum.MILLILITERS: "мл",
        }[self]
        
class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: int
    measurement: int

class RecipeIngredientRead(BaseModel):
    quantity: int
    ingredient: IngredientRead
    measurement: MeasurementEnum
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("measurement")
    def serialize_measurement(self, measurement: MeasurementEnum):
        return str(measurement)

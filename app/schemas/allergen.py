from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class AllergenBase(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Название аллергена"
    )

class AllergenCreate(AllergenBase):
    pass

class AllergenUpdate(BaseModel):
    name: Optional[str] = None

class AllergenRead(AllergenBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


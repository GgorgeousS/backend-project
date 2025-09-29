from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from typing import List
from .dependencies import SessionDep

from models.recipe import Allergen
from schemas.allergen import AllergenCreate, AllergenRead, AllergenUpdate

router = APIRouter(
    prefix="/allergens",
    tags=["allergens"],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AllergenRead)
async def create_allergen(allergen: AllergenCreate, session: SessionDep):
    db_allergen = Allergen(**allergen.model_dump())
    session.add(db_allergen)
    await session.commit()
    await session.refresh(db_allergen)
    return db_allergen

@router.get("/", response_model=List[AllergenRead])
async def read_allergens(session: SessionDep):
    stmt = select(Allergen).order_by(Allergen.id)
    allergens = await session.scalars(stmt)
    return allergens.all()

@router.get("/{allergen_id}", response_model=AllergenRead)
async def read_allergen(allergen_id: int, session: SessionDep):
    allergen = await session.get(Allergen, allergen_id)
    if not allergen:
        raise HTTPException(status_code=404, detail="Allergen not found")
    return allergen

@router.put("/{allergen_id}", response_model=AllergenRead)
async def update_allergen(allergen_id: int, allergen_update: AllergenUpdate, session: SessionDep):
    allergen = await session.get(Allergen, allergen_id)
    if not allergen:
        raise HTTPException(status_code=404, detail="Allergen not found")
    for key, value in allergen_update.model_dump(exclude_unset=True).items():
        setattr(allergen, key, value)
    await session.commit()
    await session.refresh(allergen)
    return allergen

@router.delete("/{allergen_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_allergen(allergen_id: int, session: SessionDep):
    allergen = await session.get(Allergen, allergen_id)
    if not allergen:
        raise HTTPException(status_code=404, detail="Allergen not found")
    await session.delete(allergen)
    await session.commit()

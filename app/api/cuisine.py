from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from typing import List
from .dependencies import SessionDep

from models.recipe import Cuisine
from schemas.cuisine import CuisineCreate, CuisineRead, CuisineUpdate

router = APIRouter(
    prefix="/cuisines",
    tags=["cuisines"],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CuisineRead)
async def create_cuisine(cuisine: CuisineCreate, session: SessionDep):
    db_cuisine = Cuisine(**cuisine.model_dump())
    session.add(db_cuisine)
    await session.commit()
    await session.refresh(db_cuisine)
    return db_cuisine

@router.get("/", response_model=List[CuisineRead])
async def read_cuisines(session: SessionDep):
    stmt = select(Cuisine).order_by(Cuisine.id)
    cuisines = await session.scalars(stmt)
    return cuisines.all()

@router.get("/{cuisine_id}", response_model=CuisineRead)
async def read_cuisine(cuisine_id: int, session: SessionDep):
    cuisine = await session.get(Cuisine, cuisine_id)
    if not cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")
    return cuisine

@router.put("/{cuisine_id}", response_model=CuisineRead)
async def update_cuisine(cuisine_id: int, cuisine_update: CuisineUpdate, session: SessionDep):
    cuisine = await session.get(Cuisine, cuisine_id)
    if not cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")
    for key, value in cuisine_update.model_dump(exclude_unset=True).items():
        setattr(cuisine, key, value)
    await session.commit()
    await session.refresh(cuisine)
    return cuisine

@router.delete("/{cuisine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cuisine(cuisine_id: int, session: SessionDep):
    cuisine = await session.get(Cuisine, cuisine_id)
    if not cuisine:
        raise HTTPException(status_code=404, detail="Cuisine not found")
    await session.delete(cuisine)
    await session.commit()

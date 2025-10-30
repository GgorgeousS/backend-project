from typing import Annotated
from fastapi import Depends
from models.db_helper import db_helper

from sqlalchemy.ext.asyncio import AsyncSession

SessionDep = Annotated[AsyncSession, Depends(db_helper.session_getter)]

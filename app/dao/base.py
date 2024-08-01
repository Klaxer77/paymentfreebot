from fastapi import HTTPException
from app.database import async_session_maker
from sqlalchemy import insert, select, update, delete
from app.database import engine
from sqlalchemy.exc import IntegrityError
from typing import Any, Dict, Optional, TypeVar, Union
from pydantic import BaseModel
from app.database import Base
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseDAO:
    model = None
        
    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()
        
    @classmethod
    async def find_one(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().one()
        
    @classmethod
    async def delete(cls, *filter, **filter_by) -> None:
        async with async_session_maker() as session:
            stmt = delete(cls.model).filter(*filter).filter_by(**filter_by)
            await session.execute(stmt)
        
    @classmethod
    async def find_all(cls):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns)
            result = await session.execute(query)
            return result.mappings().all()
        
    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()
            
    @classmethod
    async def update(cls, *where, **data):
        async with async_session_maker() as session:
            query = (
                update(cls.model).
                where(*where).
                values(**data).
                returning(cls.model)
            )
            result = await session.execute(query)
            await session.commit()
            return result.scalars().one()
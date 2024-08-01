from decimal import Decimal
import uuid
from app.dao.base import BaseDAO, ModelType
from app.exceptions.users.exceptions import UserNotFound
from app.users.models import Users
from app.database import async_session_maker
from sqlalchemy import select, insert, delete, update
from sqlalchemy.exc import SQLAlchemyError
from app.dao.base import CreateSchemaType
from typing import Any, Dict, Optional, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine

class UsersDAO(BaseDAO):
    model = Users
    
    @classmethod
    async def update_balance_up(cls, chat_id: int, balance: str):
        async with async_session_maker() as session:
            query = (
                update(cls.model)
                .where(cls.model.chat_id == chat_id)
                .values(balance=cls.model.balance + Decimal(balance))
            )
            await session.execute(query)
            await session.commit()
        
    @classmethod
    async def update_balance_down(cls, chat_id: int, balance: str):
        async with async_session_maker() as session:
            query = (
                update(cls.model)
                .where(cls.model.chat_id == chat_id)
                .values(balance=cls.model.balance - Decimal(balance))
            )
            await session.execute(query)
            await session.commit()
    
    @classmethod
    async def get_user(cls, user_id: uuid.UUID) -> Users:
        async with async_session_maker() as session:
            db_user = await UsersDAO.find_one_or_none(session, id=user_id)
            if db_user is None:
                raise UserNotFound
            return db_user
        
    
    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, *filter, **filter_by) -> Optional[ModelType]:
        stmt = select(cls.model).filter(*filter).filter_by(**filter_by)
        result = await session.execute(stmt)
        return result.scalars().one_or_none()
    
    @classmethod
    async def find_user(cls, **filter_by):
        async with async_session_maker() as session:
            stmt = select(cls.model).filter_by(**filter_by)
            result = await session.execute(stmt)
            return result.scalars().one_or_none()
    
    @classmethod
    async def check_user(cls, **filter_by):
        async with async_session_maker() as session:
            stmt = select(cls.model).filter_by(**filter_by)
            result = await session.execute(stmt)
            return result.scalars().one_or_none()
        
    @classmethod    
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()
            
    
    
    
    # @classmethod
    # async def find_one_or_none(cls, **filter_by):
    #     async with async_session_maker() as session:
    #         query = select(cls.model.__table__.columns).filter_by(**filter_by)
    #         result = await session.execute(query)
    #         return result.mappings().one_or_none()
        

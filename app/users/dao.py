from datetime import datetime
import uuid
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import insert, select, update, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.exceptions.base import ServerError
from app.exceptions.users.exceptions import UserNotFound
from app.notification.models import Notifications
from app.payment.models import PaymentHistory
from app.rating.models import Ratings
from app.users.models import Users
from app.logger import logger
from app.database import engine
from app.users.schemas import SUser


class UsersDAO(BaseDAO):
    model = Users
    
    @classmethod
    async def search(cls, search_field: str):
        async with async_session_maker() as session:
            query = select(Users).where(
                or_(
                    Users.first_name.ilike(f'%{search_field}%'),
                    Users.username.ilike(f'%{search_field}%')
                )
            )
            result = await session.execute(query)
            users = result.scalars().all()
            return users
        

    @classmethod
    async def update_register(cls, user_id: UUID, **data):
        try:
            extra = dict(data)
            logger.debug(msg=f"user_id = {user_id}", extra=extra)
            async with async_session_maker() as session:
                query = update(cls.model).where(cls.model.id == user_id).values(**data)
                logger.debug(
                    query.compile(engine, compile_kwargs={"literal_binds": True})
                )
                await session.execute(query)
                await session.commit()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot update register"
            extra = dict(data)
            logger.error(msg=f"{msg}, user_id = {user_id}", extra=extra, exc_info=True)
            raise ServerError

    @classmethod
    async def update_balance_up(cls, chat_id: int, balance: str):
        try:
            logger.debug(chat_id,balance)
            async with async_session_maker() as session:
                query = (
                    update(cls.model)
                    .where(cls.model.chat_id == chat_id)
                    .values(balance=cls.model.balance + Decimal(balance))
                )
                logger.debug(
                    query.compile(engine, compile_kwargs={"literal_binds": True})
                )
                await session.execute(query)
                await session.commit()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot update balance up"
            extra = {"chat_id": chat_id, "balance": balance}
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError

    @classmethod
    async def update_balance_down(cls, chat_id: int, balance: str):
        try:
            logger.debug(chat_id,balance)
            async with async_session_maker() as session:
                query = (
                    update(cls.model)
                    .where(cls.model.chat_id == chat_id)
                    .values(balance=cls.model.balance - Decimal(balance))
                )
                logger.debug(
                    query.compile(engine, compile_kwargs={"literal_binds": True})
                )
                await session.execute(query)
                await session.commit()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot update balance down"
            extra = {"chat_id": chat_id, "balance": balance}
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError

    @classmethod
    async def get_user(cls, user_id: UUID):
        try:
            logger.debug(user_id)
            async with async_session_maker() as session:
                query = select(
                    Users
                ).options(joinedload(Users.notification)).where(Users.id == user_id)
                result = await session.execute(query)
                result_orm = result.unique().scalars().all()
                
                if result_orm == []:
                    raise UserNotFound
                
                user_instance = result_orm[0]
                
                result_dto = SUser.model_validate(user_instance, from_attributes=True)
                return result_dto
                
        except UserNotFound:
            raise UserNotFound
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot get user"
            extra = {"user_id": user_id}
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, *filter, **filter_by):
        try:
            extra = dict(filter_by)
            logger.debug(msg="debug", extra=extra)
            query = select(cls.model).filter(*filter).filter_by(**filter_by)
            logger.debug(query.compile(engine, compile_kwargs={"literal_binds": True}))
            result = await session.execute(query)
            return result.scalars().one_or_none()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot find one or none"
            extra = dict(filter_by)
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError

    @classmethod
    async def find_user(cls, **filter_by):
        try:
            extra = dict(filter_by)
            logger.debug(msg="debug", extra=extra)
            async with async_session_maker() as session:
                query = select(cls.model).filter_by(**filter_by)
                logger.debug(
                    query.compile(engine, compile_kwargs={"literal_binds": True})
                )
                result = await session.execute(query)
                return result.scalars().one_or_none()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot find user"
            extra = dict(filter_by)
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError

    @classmethod
    async def check_user(cls, **filter_by):
        try:
            extra = dict(filter_by)
            logger.debug(msg="debug", extra=extra)
            async with async_session_maker() as session:
                query = select(cls.model).filter_by(**filter_by)
                logger.debug(
                    query.compile(engine, compile_kwargs={"literal_binds": True})
                )
                result = await session.execute(query)
                return result.scalars().one_or_none()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot check user"
            extra = dict(filter_by)
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError

    @classmethod
    async def add(cls, score: int, balance: Decimal, chat_id: int, username: str, first_name: str, last_name: str, is_premium: bool):
        try:
            extra = {
                "score": score,
                "chat_id": chat_id, 
                "username": username, 
                "first_name": first_name, 
                "last_name": last_name,
                "is_premium": is_premium
            }
            logger.debug(score,chat_id,username,first_name,last_name,is_premium)
            
            async with async_session_maker() as session:
                insert_user = insert(cls.model).values(
                    chat_id=chat_id,
                    balance=balance,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    is_premium=is_premium                                   
                ).returning(Users.id)
                new_user = await session.execute(insert_user)
                
                get_user_id = select(cls.model).where(cls.model.chat_id == chat_id)
                result = await session.execute(get_user_id)
                user = result.scalar_one_or_none()
                
                insert_rating = insert(Ratings).values(rated_user_id=user.id, score=score)
                await session.execute(insert_rating)
                
                insert_payment_history = insert(PaymentHistory).values( # В качестве pet проекта
                    user_id=user.id, 
                    amount=1000.00,
                    last4=4477,
                    created_at=datetime.now(),
                    action="Пополнение",
                    status="успешно"
                    )
                await session.execute(insert_payment_history)
                
                await session.commit()
                return new_user.mappings().one_or_none()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot add"
            extra = {
                "chat_id": chat_id, 
                "username": username, 
                "first_name": first_name, 
                "last_name": last_name,
                "is_premium": is_premium
            }
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError
        
                

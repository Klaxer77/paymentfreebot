import uuid
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.exceptions.base import ServerError
from app.exceptions.users.exceptions import UserNotFound
from app.notification.models import Notifications
from app.rating.models import Ratings
from app.users.models import Users
from app.logger import logger
from app.database import engine


class UsersDAO(BaseDAO):
    model = Users

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
                    Users.id,
                    Users.chat_id,
                    Users.rating,
                    Users.first_name,
                    Users.last_name,
                    Users.username,
                    Users.balance,
                    Users.frozen_balance,
                    Users.register_date,
                    Users.is_premium,
                    Notifications.accept,
                    Notifications.canceled,
                    Notifications.create,
                    Notifications.conditions_are_met
                ).where(Users.id == user_id).join(
                        Notifications,
                        Notifications.user_id == Users.id,
                        isouter=True,
                    )
                result = await session.execute(query)
                users = result.mappings().all()
                user = users[0]
                formatted_result = {
                "id": user.id,
                "chat_id": user.chat_id,
                "rating": user.rating,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "balance": user.balance,
                "frozen_balance": user.frozen_balance,
                "is_premium": user.is_premium,
                "register_date": user.register_date,
                "notification": {
                    "accept": user.accept,
                    "canceled": user.canceled,
                    "create": user.create,
                    "conditions_are_met": user.conditions_are_met
                    }
                }
                return formatted_result
            
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
    async def add(cls, score: int, chat_id: int, username: str, first_name: str, last_name: str, is_premium: bool):
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

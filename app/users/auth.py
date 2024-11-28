import asyncio
import json
from typing import Union
from uuid import UUID
import uuid
from jose import jwt
from passlib.context import CryptContext

from app.config import settings
from app.exceptions.schemas import SExceptionsINFO
from app.logger import logger
from app.notification.dao import NotificationDAO
from app.users.dao import UsersDAO
from app.users.schemas import SUserRegisterANDlogin
import secrets

from app.utils.redis import AsyncRedis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(chat_id: int) -> str:
    to_encode = {"sub": str(chat_id)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    logger.debug(encoded_jwt)
    return encoded_jwt

async def send_event_to_subscribers(data: str, event: str):
    async with AsyncRedis() as redis:
        event_data = json.dumps({
            "id": str(secrets.token_hex(16)),
            "event": event,
            "data": data
        })

        subscribers = await redis.smembers("subscribers_set")

        for queue in subscribers:
            await redis.lpush(queue, event_data)

        return None




async def register(user_data: SUserRegisterANDlogin) -> None | SExceptionsINFO:
    user = await UsersDAO.check_user(username=user_data.username)

    if user is None:
        new_user = await UsersDAO.add(
            score=5.0,
            balance=1000.00, # В качестве pet проекта
            chat_id=user_data.chat_id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_premium=user_data.is_premium,
        )
        await NotificationDAO.add(user_id=new_user.id)
        return new_user

    if any(
        [
            user.chat_id != user_data.chat_id,
            user.username != user_data.username,
            user.first_name != user_data.first_name,
            user.last_name != user_data.last_name,
            user.is_premium != user_data.is_premium,
        ]
    ):
        new_user = await UsersDAO.update_register(
            user_id=user.id,
            chat_id=user_data.chat_id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_premium=user_data.is_premium,
        )
        return new_user

    return user

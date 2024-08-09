from jose import jwt
from passlib.context import CryptContext

from app.config import settings
from app.exceptions.schemas import SExceptionsINFO
from app.logger import logger
from app.notification.dao import NotificationDAO
from app.users.dao import UsersDAO
from app.users.schemas import SUserRegisterANDlogin


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(chat_id: int) -> str:
    to_encode = {"sub": str(chat_id)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    logger.debug(encoded_jwt)
    return encoded_jwt


async def register(user_data: SUserRegisterANDlogin) -> None | SExceptionsINFO:
    user = await UsersDAO.check_user(username=user_data.username)

    if user is None:
        new_user = await UsersDAO.add(
            score=5,
            chat_id=user_data.chat_id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_premium=user_data.is_premium,
        )
        await NotificationDAO.add(user_id=new_user.id)
        return None

    if any(
        [
            user.chat_id != user_data.chat_id,
            user.username != user_data.username,
            user.first_name != user_data.first_name,
            user.last_name != user_data.last_name,
            user.is_premium != user_data.is_premium,
        ]
    ):
        await UsersDAO.update_register(
            user_id=user.id,
            chat_id=user_data.chat_id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_premium=user_data.is_premium,
        )
        return None

    return None

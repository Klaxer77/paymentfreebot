from fastapi import Depends, Request
from jose import ExpiredSignatureError, JWTError, jwt

from app.config import settings
from app.exceptions.base import ServerError
from app.exceptions.users.exceptions import (
    IncorrectTokenFormatException,
    NoneToken,
    TokenExpiredException,
    UserIsNotPresentException,
)
from app.users.dao import UsersDAO
from app.logger import logger


def get_token(request: Request):
    auth_header = request.headers.get("Authorization")
    logger.debug(auth_header)
    if not auth_header:
        raise NoneToken
    token = auth_header.split()[1]
    logger.debug(token)
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        msg = "JWT Exc: cannot get current user"
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
    except ExpiredSignatureError:
        extra = {"token": token}
        logger.error(msg=msg, extra=extra, exc_info=True)
        raise TokenExpiredException
    except JWTError:
        extra = {"token": token}
        logger.error(msg=msg, extra=extra, exc_info=True)
        raise IncorrectTokenFormatException
    chat_id: str = payload.get("sub")
    logger.debug(chat_id)
    if not chat_id:
        raise UserIsNotPresentException
    user = await UsersDAO.find_user(chat_id=int(chat_id))
    if not user:
        raise UserIsNotPresentException

    return user

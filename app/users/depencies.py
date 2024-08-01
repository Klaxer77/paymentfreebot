from typing import Optional
import uuid
from fastapi import Depends, HTTPException, Request, status
from jose import ExpiredSignatureError, JWTError, jwt
from typing import Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param

from app.config import settings
from app.users.models import Users
from app.users.dao import UsersDAO
from app.exceptions.users.exceptions import IncorrectTokenFormatException, IncorrectTokenHeaders, InvalidTokenException, NoneToken, TokenExpiredException, UserCheckAdminRole, UserIsNotPresentException


def get_token(request: Request):
    try:
        token = request.headers.get("Authorization")
        if not token:
            raise NoneToken
        return token
    except Exception:
        raise IncorrectTokenHeaders

async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except ExpiredSignatureError:
        raise TokenExpiredException
    except JWTError:
        raise IncorrectTokenFormatException
    chat_id: str = payload.get("sub")
    if not chat_id:
        raise UserIsNotPresentException
    user = await UsersDAO.find_one_or_none(chat_id=int(chat_id))
    if not user:
        raise UserIsNotPresentException

    return user

async def get_current_user_method(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except ExpiredSignatureError:
        raise TokenExpiredException
    except JWTError:
        raise IncorrectTokenFormatException
    chat_id: str = payload.get("sub")
    if not chat_id:
        raise UserIsNotPresentException
    user = await UsersDAO.find_user(chat_id=int(chat_id))
    if not user:
        raise UserIsNotPresentException

    return user
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Response

from app.config import settings
from app.exceptions.base import ServerError
from app.exceptions.schemas import SExceptionsINFO
from app.exceptions.users.exceptions import UserNotFound
from app.users.auth import create_access_token
from app.users.dao import UsersDAO
from app.users.depencies import get_current_user
from app.users.schemas import SCreateToken, SToken, SUser, SUserDetail, SUserListALL, SUserRegisterANDlogin
from sqlalchemy.exc import SQLAlchemyError
from app.logger import logger
from app.utils.security import security


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/create/token")
async def create_token(response: Response, request: Request, user: SCreateToken) -> SToken | SExceptionsINFO:
    """
    **Создать токен для аутентификации пользователя**

    **Args**

    `username` - username пользователя в telegram

    **Returns**

    Возвращает токен для аутентификации

    **Note**

    Пользователь должен быть зарегистрирован в боте с данным _username_

    """

    try:
        check_user = await UsersDAO.check_user(username=user.username)
        if not check_user:
            raise UserNotFound
        token = create_access_token(check_user.chat_id)
        logger.debug(token)
        return {"token": token}
    
    except UserNotFound as e:
        return {"detail": e.detail}
    except (SQLAlchemyError, Exception) as e:
        if isinstance(e, SQLAlchemyError):
            msg = "Database Exc"
        if isinstance(e, Exception):
            msg = "Unknown Exc"
        msg += ": cannot return token"
        logger.error(msg=msg, exc_info=True)
        raise ServerError


@router.get("/search/{search}")
async def search(search: str) -> list[SUserListALL]:
    """ 
    **Поиск по пользователям**
    
    **Args**
    
    `search` - @username или first_name пользователя
    
    **Returns**
    
    Возвращает одного или несколько пользователей
    
    """
    search_user = await UsersDAO.search(search)
    return search_user


@router.get("/all")
async def all() -> list[SUserListALL]:
    """
    **Просмотр всех пользователей**

    **Returns**:

    Возвращает актуальную информацию о всех пользователях.
    """
    return await UsersDAO.find_all()


@router.get("/me")
async def read_user_me(
authorization: str = Depends(security),
user: SUser = Depends(get_current_user)
) -> SUser | SExceptionsINFO:
    """
    **Просмотр профиля**

    **Headers**:

    Authorization: _access token_ *required

    **Returns**:

    Возвращает актуальную информацию о профиле пользователя.
    """
    user = await UsersDAO.get_user(user_id=user.id)
    return user

@router.get("/detail/{user_id}")
async def user_detail(user_id: UUID) -> SUserDetail | SExceptionsINFO:
    """
    **Просмотр конкретного пользователя**
    
    **Args**
    
    `user_id` - id просматриваемого пользователя
    
    **Returns**
    
    Возвращает информацию о просматриваемом пользователе
     
    """
    user = await UsersDAO.get_user(user_id=user_id)
    return user


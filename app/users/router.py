from uuid import UUID
from fastapi import APIRouter, Depends

from app.config import settings
from app.exceptions.schemas import SExceptionsINFO
from app.users.dao import UsersDAO
from app.users.depencies import get_current_user
from app.users.schemas import SUser, SUserDetail, SUserListALL, SUserRegisterANDlogin

router = APIRouter(prefix="/auth", tags=["Auth"])


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
user: SUser = Depends(get_current_user)
) -> SUser | SExceptionsINFO:
    """
    **Просмотр профиля**

    **Headers**:

    Authorization: _access token_ *required

    **Returns**:

    Возвращает актуальную информацию о профиле пользователя.
    """
    return user

@router.get("/{user_id}")
async def user_detail(user_id: UUID) -> SUserDetail | SExceptionsINFO:
    user = await UsersDAO.get_user(user_id=user_id)
    return user

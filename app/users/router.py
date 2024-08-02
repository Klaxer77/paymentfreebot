from fastapi import APIRouter, Depends, Request
from app.users.depencies import get_current_user, get_current_user_method
from app.users.dao import UsersDAO
from app.users.schemas import SUser, SUserRegisterANDlogin
from app.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register")
async def register(user_data: SUserRegisterANDlogin):
    user = await UsersDAO.check_user(username=user_data.username)
    if user: 
        return None
    await UsersDAO.add(
        chat_id=user_data.chat_id,
        username=user_data.username, 
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_premium=user_data.is_premium
    )
    return None
   
@router.get("/all")
async def all() -> list[SUser]:
    return await UsersDAO.find_all()

@router.get("/me")
async def read_user_me(request: Request) -> SUser:
    token = request.cookies.get("token")
    if settings.MODE in ["DEV", "TEST"]:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Njg2NTg1NTQifQ.P57B4IgT6OVPYfwgT2apu7B6B2TFW_5i31glrKjXHRw"
    user = await get_current_user_method(token)
    if not user:
        return []
    return user
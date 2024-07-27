from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from app.exceptions.schemas import SExceptions
from app.users.depencies import get_current_user, get_token
from app.users.models import Users
from app.users.dao import UsersDAO
from app.users.schemas import STokens, SUser, SUserRegisterANDlogin
from app.exceptions.users.exceptions import UserISexists, UserISerror
from app.users.auth import create_access_token
from app.config import settings

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)



@router.post('/register')
async def register(user_data: SUserRegisterANDlogin):
    user = await UsersDAO.check_user(username=user_data.username)
    if user: 
        return None
    await UsersDAO.add(
        chat_id=user_data.chat_id,
        username=user_data.username, 
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    return None
   

@router.get('/me')
async def read_user_me(user: str = Depends(get_current_user)):
    return user
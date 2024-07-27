from fastapi import APIRouter, Depends
from app.users.depencies import get_current_user
from app.users.dao import UsersDAO
from app.users.schemas import SUserRegisterANDlogin

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
        last_name=user_data.last_name,
        is_premium=user_data.is_premium
    )
    return None
   

@router.get('/me')
async def read_user_me(user: str = Depends(get_current_user)):
    return user
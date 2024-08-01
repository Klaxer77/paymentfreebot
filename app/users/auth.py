import uuid
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
from app.config import settings
from app.users.dao import UsersDAO
from app.exceptions.users.exceptions import UserISerror
from app.database import async_session_maker
from app.users.schemas import SToken
from app.exceptions.users.exceptions import InvalidTokenException, TokenExpiredException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(chat_id: int) -> str:
        to_encode = {
            "sub": str(chat_id)
            # "exp": datetime.utcnow() + timedelta(
            #     minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

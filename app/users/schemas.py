from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
    
class SUser(BaseModel):
    first_name: str
    last_name: str | None
    username: str
    is_premium: bool | None
    
class SUserRegisterANDlogin(BaseModel):
    chat_id: int
    first_name: str
    last_name: str | None
    username: str
    is_premium: bool | None
    
class SToken(BaseModel):
    token: str
    
    
    
from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
    
class SUser(BaseModel):
    first_name: str
    last_name: str | None
    username: str
    is_premium: bool
    
class SUserRegisterANDlogin(BaseModel):
    chat_id: int
    first_name: str
    last_name: str | None
    username: str
    is_premium: bool
    
class RefreshSessionCreate(BaseModel):
    refresh_token: uuid.UUID
    expires_in: int
    user_id: uuid.UUID
    
class SToken(BaseModel):
    token: str
    
class STokens(BaseModel):
    access_token: str
    refresh_token: uuid.UUID
    
class RefreshSessionUpdate(RefreshSessionCreate):
    user_id: Optional[uuid.UUID] = Field(None)
    
class CsrfSettings(BaseModel):
  secret_key:str = 'asecrettoeverybody'
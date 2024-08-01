from decimal import Decimal
from typing import Optional
import uuid
from pydantic import BaseModel, field_validator
from datetime import datetime
from uuid import UUID
    
class SUser(BaseModel):
    id: UUID
    chat_id: int
    first_name: str
    username: str
    frozen_balance: Decimal
    register_date: datetime
    last_name: str | None
    balance: Decimal
    is_premium: bool | None
    
    @field_validator("register_date")
    @classmethod
    def check_register_date(cls, v: datetime):
        v = v.strftime("%d-%m-%Y %H:%M")
        return v
    
class SUserRegisterANDlogin(BaseModel):
    chat_id: int
    first_name: str
    last_name: str | None
    username: str
    is_premium: bool | None
    
class SToken(BaseModel):
    token: str
    
    
    
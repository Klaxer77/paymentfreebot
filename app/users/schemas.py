from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, field_validator


class SUserListALL(BaseModel):
    id: UUID
    rating: float
    first_name: str
    last_name: str | None
    username: str
    is_premium: bool | None
    
class SUserDetail(SUserListALL):
    pass

class SNotification(BaseModel):
    accept: bool
    canceled: bool
    create: bool
    conditions_are_met: bool


class SUser(BaseModel):
    id: UUID
    chat_id: int
    rating: float
    first_name: str
    last_name: str | None
    username: str
    balance: Decimal
    frozen_balance: Decimal
    is_premium: bool | None
    register_date: datetime
    notification: SNotification



class SUserRegisterANDlogin(BaseModel):
    chat_id: int
    first_name: str
    last_name: str | None
    username: str
    is_premium: bool | None


class SToken(BaseModel):
    token: str

class SCreateToken(BaseModel):
    chat_id: int
    
    

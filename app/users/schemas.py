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


class SUser(BaseModel):
    id: UUID
    rating: float
    chat_id: int
    first_name: str
    last_name: str | None
    username: str
    frozen_balance: Decimal
    balance: Decimal
    register_date: datetime
    is_premium: bool | None

    @field_validator("register_date")
    @classmethod
    def check_register_date(cls, v):
        if isinstance(v, str):
            v = datetime.strptime(v, "%d-%m-%Y %H:%M")
        return v


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
    

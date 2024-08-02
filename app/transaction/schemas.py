from datetime import datetime
from decimal import Decimal
from uuid import UUID
from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator


class STransactionCreate(BaseModel):
    user_for: UUID
    sum: Decimal
    
    @field_validator("sum")
    @classmethod
    def check_sum(cls, v: str):
        if v < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Сумма сделки должна быть не менее 100р")
        return v
    
class STransactionList(BaseModel):
    id: UUID
    sum: Decimal
    status: str
    created_at: datetime
    finished_at: datetime | None
    first_name: str
    last_name: str | None
    username: str
    is_premium: bool | None
    
    @field_validator("created_at")
    @classmethod
    def check_created_at(cls, v):
        if isinstance(v, str):
            v = datetime.strptime(v, "%d-%m-%Y %H:%M")
        return v
    
    @field_validator("finished_at")
    @classmethod
    def check_finished_at(cls, v):
        if v is not None and isinstance(v, str):
            v = datetime.strptime(v, "%d-%m-%Y %H:%M")
        return v
    
class STransaction(BaseModel):
    transaction_id: UUID
    
class STransactionINFO(BaseModel):
    detail: str
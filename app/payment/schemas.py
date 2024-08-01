from datetime import datetime
from decimal import Decimal
from uuid import UUID
from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator
from app.config import settings



class SPaymentCreate(BaseModel):
    amount: Decimal
    
    @field_validator("amount")
    @classmethod
    def check_amount(cls, v: Decimal):
        if v < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Минимальная сумма пополнения 10р")
        if v > 350000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Максимальная сумма пополнения за раз 350.000р")
        return v
    
class SPaymentPayout(BaseModel):
    card_number: int
    amount: Decimal
    
    @field_validator("amount")
    @classmethod
    def check_amount(cls, v: Decimal):
        if v < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Минимальная сумма вывода 10р")
        if v > 500000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Максимальная сумма вывода за раз 500.000р")
        return v
    
class SPaymentList(BaseModel):
    id: int
    user_id: UUID
    amount: Decimal
    last4: int
    created_at: datetime
    action: str
    status: str
    
    @field_validator("created_at")
    @classmethod
    def check_created_at(cls, v: datetime):
        v = v.strftime("%d-%m-%Y %H:%M")
        return v
    
    
class SPaymentINFO(BaseModel):
    detail: str
    
class SPaymentConfirmURL(BaseModel):
    url: str
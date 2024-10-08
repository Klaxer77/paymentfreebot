from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator


class SPaymentCreate(BaseModel):
    amount: Decimal

    @field_validator("amount")
    @classmethod
    def check_amount(cls, v: Decimal):
        if v < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Минимальная сумма пополнения 10р",
            )
        if v > 350000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Максимальная сумма пополнения за раз 350.000р",
            )
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
                detail="Минимальная сумма вывода 10р",
            )
        if v > 500000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Максимальная сумма вывода за раз 500.000р",
            )
        return v


class SPaymentList(BaseModel):
    id: UUID
    user_id: UUID
    amount: Decimal
    last4: int
    created_at: datetime
    action: str
    status: str



class SPaymentConfirmURL(BaseModel):
    url: str

from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status, Request
from datetime import datetime
from app.exceptions.transaction.exeptions import TransactionCreated, TransactionErrorInitiator, TransactionExceedsBalance, TransactionLimitBalance, TransactionNotTheInitiator, TransactionStatusActive, TransactionStatusActiveTrue, TransactionStatusCanceled, TransactionStatusCanceledTrue, TransactionStatusPending, TransactionUserError, TransactionStatusСompleted, TransactionСonditionsAreMet
from app.transaction.dao import TransactionDAO
from app.transaction.schemas import STransaction, STransactionCreate, STransactionINFO, STransactionList
from app.users.dao import UsersDAO
from app.users.depencies import get_current_user_method
from app.bot import bot
from app.config import settings

router = APIRouter(
    prefix="/transaction",
    tags=["Transaction"]
)

@router.post("/create")
async def create(request: Request, transaction: STransactionCreate) -> STransactionINFO:
    token = request.cookies.get("token")
    if settings.MODE in ["DEV", "TEST"]:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Njg2NTg1NTQifQ.P57B4IgT6OVPYfwgT2apu7B6B2TFW_5i31glrKjXHRw"

    user = await get_current_user_method(token)
    
    if not user:
        return []
    user = await UsersDAO.get_user(user.id)
    # user.id = "74957fa5-f010-4b8b-b2f4-4ccc28d71be5"
    if transaction.user_for == user.id:
        raise TransactionUserError
    
    if user.balance < transaction.sum:
        raise TransactionExceedsBalance
     
    model = await TransactionDAO.add(initiator=user.id, user_for=transaction.user_for, sum=transaction.sum, status="в ожидании", creator=user.id)
    user_for = await UsersDAO.get_user(model.user_for)
    send_user = user_for.chat_id
    
    if settings.MODE in ["DEV", "TEST"]:
        send_user = user.chat_id
        
    await bot.send_message(send_user, text=f"⭐️ У вас новая заявка на сделку с {user.first_name} | @{user.username}\nСумма: {model.sum}")
    raise TransactionCreated

@router.post("/canceled")
async def canceled(transaction: STransaction) -> STransactionINFO:
    current_transaction = await TransactionDAO.get_users(transaction_id=transaction.transaction_id)
    if current_transaction.status == "отменено":
        raise TransactionStatusCanceled
    if current_transaction.status == "завершено":
        raise TransactionStatusСompleted
    if current_transaction.status == "активно":
        await TransactionDAO.canceled(
            transaction_id=transaction.transaction_id, 
            status="отменено", 
            chat_id_initiator=current_transaction.initiator_chat_id,
            chat_id_user_for=current_transaction.user_for_chat_id,
            balance=current_transaction.sum
        )
        raise TransactionStatusCanceledTrue
    await TransactionDAO.update_status(transaction_id=transaction.transaction_id, status="отменено")
    raise TransactionStatusCanceledTrue

@router.post("/accept")
async def accept(request: Request, transaction: STransaction) -> STransactionINFO:
    token = request.cookies.get("token")
    if settings.MODE in ["DEV", "TEST"]:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Njg2NTg1NTQifQ.P57B4IgT6OVPYfwgT2apu7B6B2TFW_5i31glrKjXHRw"
    user = await get_current_user_method(token)
    if not user:
        return []
    # user.id = "74957fa5-f010-4b8b-b2f4-4ccc28d71be5"
    current_transaction = await TransactionDAO.get_users(transaction_id=transaction.transaction_id)
    if current_transaction.status == "активно":
        raise TransactionStatusActive
    if current_transaction.status == "завершено":
        raise TransactionStatusСompleted
    if current_transaction.status == "отменено":
        raise TransactionStatusCanceled
    if str(current_transaction.initiator) == str(user.id):
        raise TransactionErrorInitiator
    
    await TransactionDAO.accept(
        transaction_id=transaction.transaction_id, 
        status="активно", 
        chat_id_initiator=current_transaction.initiator_chat_id,
        chat_id_user_for=current_transaction.user_for_chat_id,
        balance=current_transaction.sum
    )
    raise TransactionStatusActiveTrue

@router.post("/conditions_are_met")
async def conditions_are_met(request: Request, transaction: STransaction):
    token = request.cookies.get("token")
    if settings.MODE in ["DEV", "TEST"]:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Njg2NTg1NTQifQ.P57B4IgT6OVPYfwgT2apu7B6B2TFW_5i31glrKjXHRw"
    user = await get_current_user_method(token)
    if not user:
        return []
    current_transaction = await TransactionDAO.get_users(transaction_id=transaction.transaction_id)
    if user.chat_id != current_transaction.initiator_chat_id:
        raise TransactionNotTheInitiator
    if current_transaction.status == "в ожидании":
        raise TransactionStatusPending
    if current_transaction.status == "завершено":
        raise TransactionStatusСompleted
    if current_transaction.status == "отменено":
        raise TransactionStatusCanceled
    await TransactionDAO.conditions_are_met(
        transaction_id=transaction.transaction_id, 
        status="завершено", 
        chat_id_initiator=current_transaction.initiator_chat_id,
        chat_id_user_for=current_transaction.user_for_chat_id,
        balance=current_transaction.sum
    )
    raise TransactionСonditionsAreMet

@router.get("/list_with_status/{statuses}")
async def list_with_status(
    request: Request, 
    statuses: str) -> list[STransactionList]:
    """ 
    
    **Args**:
    
    `creator.chat_id` - id чата создателя сделки. Нужен, чтобы отобразить кнопку принятия сделки, сравнив с `user_for.chat_id`.
    
    `statuses` - статус фильтры, передаются через запятую (например: "в ожидании,завершено").
    
    **Returns**: 
    
    Возвращает все сделки с пользователями по статусу.
    
    **Note**: 
    
    Возможные статусы: _в ожидании_, _завершено_, _активно_, _отменено_.
    """
    token = request.cookies.get("token")
    if settings.MODE in ["DEV", "TEST"]:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Njg2NTg1NTQifQ.P57B4IgT6OVPYfwgT2apu7B6B2TFW_5i31glrKjXHRw"
    
    user = await get_current_user_method(token)
    if not user:
        return []
    
    status_list = [status.strip() for status in statuses.split(',')]

    return await TransactionDAO.list_with_status(user_id=user.id, statuses=status_list)
    
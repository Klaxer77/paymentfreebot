from fastapi import APIRouter, HTTPException, status, Request
from datetime import datetime
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
async def create(request: Request, transaction: STransactionCreate) -> STransactionINFO | None:
    token = request.cookies.get("token")
    if settings.MODE in ["DEV", "TEST"]:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Njg2NTg1NTQifQ.P57B4IgT6OVPYfwgT2apu7B6B2TFW_5i31glrKjXHRw"

    user = await get_current_user_method(token)
    
    if not user:
        return None
    user = await UsersDAO.get_user(user.id)
    
    if user.balance < transaction.sum:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Сумма сделки превышает текущий баланс")
    
    model = await TransactionDAO.add(initiator=user.id, user_for=transaction.user_for, sum=transaction.sum, status="в ожидании")
    user_for = await UsersDAO.get_user(model.user_for)
    send_user = user_for.chat_id
    
    if settings.MODE in ["DEV", "TEST"]:
        send_user = user.chat_id
        
    await bot.send_message(send_user, text=f"⭐️ У вас новая заявка на сделку с {user.first_name} | @{user.username}\nСумма: {model.sum}")
    raise HTTPException(status_code=status.HTTP_201_CREATED, detail="Сделка создана")

@router.post("/canceled")
async def canceled(transaction: STransaction) -> STransactionINFO:
    current_transaction = await TransactionDAO.get_users(transaction_id=transaction.id)
    if current_transaction.status == "активно":
        await TransactionDAO.canceled(
            transaction_id=transaction.id, 
            status="отменено", 
            chat_id_initiator=current_transaction.initiator_chat_id,
            chat_id_user_for=current_transaction.user_for_chat_id,
            balance=current_transaction.sum
        )
        raise HTTPException(status_code=status.HTTP_200_OK, detail=f"Сделка с {current_transaction.user_for_first_name} отменена")
    await TransactionDAO.update_status(transaction_id=transaction.id, status="отменено")
    raise HTTPException(status_code=status.HTTP_200_OK, detail=f"Сделка с {current_transaction.user_for_first_name} отменена")

@router.post("/accept")
async def accept(transaction: STransaction) -> STransactionINFO:
    current_transaction = await TransactionDAO.get_users(transaction_id=transaction.id)
    if current_transaction.status == "активно":
        raise HTTPException(status_code=status.HTTP_201_CREATED, detail=f"Сделка с {current_transaction.user_for_first_name} уже активна")
    await TransactionDAO.accept(
        transaction_id=transaction.id, 
        status="активно", 
        chat_id_initiator=current_transaction.initiator_chat_id,
        chat_id_user_for=current_transaction.user_for_chat_id,
        balance=current_transaction.sum
    )
    raise HTTPException(status_code=status.HTTP_201_CREATED, detail=f"Сделка с {current_transaction.user_for_first_name} принята")

@router.get("/history")
async def history(request: Request) -> list[STransactionList] | None:
    token = request.cookies.get("token")
    if settings.MODE in ["DEV", "TEST"]:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Njg2NTg1NTQifQ.P57B4IgT6OVPYfwgT2apu7B6B2TFW_5i31glrKjXHRw"
    user = await get_current_user_method(token)
    if not user:
        return None
    return await TransactionDAO.history_list(initiator=user.id)
    
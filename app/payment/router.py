from fastapi import APIRouter, Depends, Request, HTTPException, status
from datetime import datetime, timedelta
from app.payment.dao import PaymentDAO
from app.payment.schemas import SPaymentConfirmURL, SPaymentCreate, SPaymentList, SPaymentPayout, SPaymentINFO
from app.users.dao import UsersDAO
from app.users.depencies import get_current_user_method
from app.utils.translator import translator
from app.config import settings

router = APIRouter(
    prefix='/payment',
    tags=['Payment']
)


@router.post("/webhook/payout")
async def webhook_payout(request: Request) -> None:
    token = request.cookies.get("token")
    if settings.MODE in ["DEV", "TEST"]:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Njg2NTg1NTQifQ.P57B4IgT6OVPYfwgT2apu7B6B2TFW_5i31glrKjXHRw"
    user = await get_current_user_method(token)
    if not user:
        return None
    
    response = await request.json()
    
    status = response["object"]["status"]
    amount = response["object"]["amount"]["value"]
    last4 = response["object"]["payout_destination"]["card"]["last4"]
    created_at = response["object"]["created_at"]
    
    time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    dt = datetime.strptime(created_at, time_format)
    new_time = dt + timedelta(hours=5)
    
    if status == "succeeded":
        await UsersDAO.update_balance_down(chat_id=user.chat_id, balance=str(amount))
    await PaymentDAO.add(user_id=user.id,amount=amount,last4=int(last4),created_at=new_time,action="Вывод",status=translator.translate(status))
    return None
    
@router.post("/webhook/create")
async def webhook_payout(request: Request) -> None:
    token = request.cookies.get("token")
    if settings.MODE in ["DEV", "TEST"]:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Njg2NTg1NTQifQ.P57B4IgT6OVPYfwgT2apu7B6B2TFW_5i31glrKjXHRw"
    user = await get_current_user_method(token)
    if not user:
        return None
    
    response = await request.json()
    
    status = response["object"]["status"]
    amount = response["object"]["amount"]["value"]
    last4 = response["object"]["payment_method"]["card"]["last4"]
    captured_at = response["object"]["captured_at"]

    time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    dt = datetime.strptime(captured_at, time_format)
    new_time = dt + timedelta(hours=5)
    
    if status == "succeeded":
        await UsersDAO.update_balance_up(chat_id=user.chat_id, balance=str(amount))
    await PaymentDAO.add(user_id=user.id,amount=amount,last4=int(last4),created_at=new_time,action="Пополнение",status=translator.translate(status))
    return None


@router.post('/create')
async def create(payment: SPaymentCreate) -> SPaymentConfirmURL:
    url = await PaymentDAO.create(payment.amount)
    return {"url": url}
    

@router.post('/payout')
async def payout(request: Request, payment: SPaymentPayout) -> SPaymentINFO:
    token = request.cookies.get("token")
    if settings.MODE in ["DEV", "TEST"]:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Njg2NTg1NTQifQ.P57B4IgT6OVPYfwgT2apu7B6B2TFW_5i31glrKjXHRw"
    user = await get_current_user_method(token)
    if not user:
        return []
    
    if user.balance < payment.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Баланс меньше суммы вывода")
    await PaymentDAO.payout(payment.amount, payment.card_number)
    raise HTTPException(status_code=status.HTTP_201_CREATED, detail="Заявка на вывод отправлена")


@router.get("/history")
async def history(request: Request) -> list[SPaymentList]:
    token = request.cookies.get("token")
    if settings.MODE in ["DEV", "TEST"]:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5Njg2NTg1NTQifQ.P57B4IgT6OVPYfwgT2apu7B6B2TFW_5i31glrKjXHRw"
    user = await get_current_user_method(token)
    if not user:
        return []
    return await PaymentDAO.find_one_or_none(user_id=user.id)

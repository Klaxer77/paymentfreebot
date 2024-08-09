from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.config import settings
from app.exceptions.schemas import SExceptionsINFO
from app.payment.dao import PaymentDAO
from app.payment.schemas import (
    SPaymentConfirmURL,
    SPaymentCreate,
    SPaymentList,
    SPaymentPayout,
)
from app.users.dao import UsersDAO
from app.users.depencies import get_current_user
from app.users.schemas import SUser
from app.utils.translator import translator

router = APIRouter(prefix="/payment", tags=["Payments"])


@router.post("/webhook/payout")
async def webhook_payout(request: Request) -> None:
    """

    `Only Webhook URL`

    """
    response = await request.json()

    status = response["object"]["status"]
    amount = response["object"]["amount"]["value"]
    last4 = response["object"]["payout_destination"]["card"]["last4"]
    created_at = response["object"]["created_at"]
    user_id = response["object"]["metadata"]["user_id"]
    chat_id = response["object"]["metadata"]["chat_id"]

    time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    dt = datetime.strptime(created_at, time_format)
    new_time = dt + timedelta(hours=5)

    if status == "succeeded":
        await UsersDAO.update_balance_down(chat_id=int(chat_id), balance=str(amount))
    await PaymentDAO.add(
        user_id=UUID(user_id),
        amount=amount,
        last4=int(last4),
        created_at=new_time,
        action="Вывод",
        status=translator.translate(status),
    )
    return Response(status_code=200)


@router.post("/webhook/create")
async def webhook_payout(request: Request) -> None:
    """

    `Only Webhook URL`

    """

    response = await request.json()

    status = response["object"]["status"]
    amount = response["object"]["amount"]["value"]
    last4 = response["object"]["payment_method"]["card"]["last4"]
    captured_at = response["object"]["captured_at"]
    user_id = response["object"]["metadata"]["user_id"]
    chat_id = response["object"]["metadata"]["chat_id"]

    time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    dt = datetime.strptime(captured_at, time_format)
    new_time = dt + timedelta(hours=5)

    if status == "succeeded":
        await UsersDAO.update_balance_up(chat_id=int(chat_id), balance=str(amount))
    await PaymentDAO.add(
        user_id=UUID(user_id),
        amount=amount,
        last4=int(last4),
        created_at=new_time,
        action="Пополнение",
        status=translator.translate(status),
    )
    return Response(status_code=200)


@router.post("/create")
async def create(
    payment: SPaymentCreate,
    user: SUser = Depends(get_current_user),
) -> SPaymentConfirmURL  | SExceptionsINFO:
    """
    **Пополнить баланс**

    **Headers**:

    Authorization: _access token_ *required

    **Args**:

    `amount` - сумма пополнения _min: 10_  |  _max: 350.000_.  _Тестовый номер карты_: 5555555555554477 (Пополнить этой картой)

    **Returns**:

    Возвращает url на котором проводятся дальнейшие операции с платежом.

    """
    metadata = {
        "user_id": str(user.id),
        "chat_id": user.chat_id,
    }
    url = await PaymentDAO.create(payment.amount, metadata=metadata)
    return {"url": url}


@router.post("/payout")
async def payout(
    payment: SPaymentPayout,
    user: SUser = Depends(get_current_user),
) ->  SExceptionsINFO:
    """
    **Вывести средства**

    **Headers**:

    Authorization: _access token_ *required

    **Args**:

    `card_number` - номер карты на которую поступят средства. _Тестовый номер карты:_ 5555555555554477

    `amount` - сумма вывода _min: 10_  |  _max: 500.000_

    **Returns**:

    Возвращает актуальную информацию о платеже.

    """
    metadata = {
        "user_id": str(user.id),
        "chat_id": user.chat_id,
    }
    if user.balance < payment.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Баланс меньше суммы вывода"
        )
    await PaymentDAO.payout(payment.amount, payment.card_number, metadata=metadata)
    raise HTTPException(
        status_code=status.HTTP_201_CREATED, detail="Заявка на вывод отправлена"
    )


@router.get("/history")
async def history(
user: SUser = Depends(get_current_user)
) -> list[SPaymentList]  | SExceptionsINFO:
    """
    **Просмотр истории платежей пользователя**

    **Headers**:

    Authorization: _access token_ *required

    **Returns**:

    Возвращает актуальную информацию о всех платежах пользователя.
    """
    return await PaymentDAO.find_one_or_none(user_id=user.id)

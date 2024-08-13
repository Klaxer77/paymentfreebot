from decimal import Decimal
from typing import Optional
from uuid import UUID
from aiogram.exceptions import TelegramBadRequest

from fastapi import APIRouter, Depends, Request, HTTPException, status

from app.bot import bot
from app.config import settings
from app.exceptions.base import TelegramError
from app.exceptions.schemas import SExceptionsINFO
from app.exceptions.transaction.exeptions import (
    TransactionCreated,
    TransactionErrorInitiator,
    TransactionErrorInitiatorOrUserFor,
    TransactionExceedsBalance,
    TransactionNotFound,
    TransactionNotTheInitiator,
    TransactionStatusActive,
    TransactionStatusActiveTrue,
    TransactionStatusCanceled,
    TransactionStatusCanceledTrue,
    TransactionStatusPending,
    TransactionStatusСompleted,
    TransactionUserError,
    TransactionСonditionsAreMet,
)
from app.exceptions.users.exceptions import UserNotFound
from app.rating.dao import RatingDAO
from app.transaction.dao import TransactionDAO
from app.transaction.schemas import (
    STransaction,
    STransactionCreate,
    STransactionList,
)
from app.users.dao import UsersDAO
from app.users.depencies import get_current_user
from app.users.schemas import SUser
from app.logger import logger


router = APIRouter(prefix="/transaction", tags=["Transactions"])


@router.post("/create")
async def create(
    transaction: STransactionCreate,
    user: SUser = Depends(get_current_user),
) -> SExceptionsINFO:
    """
    **Создать сделку**

    **Headers**:

    Authorization: _access token_ *required

    **Args**:

    `user_for` - id пользователя , которому нужно отправить запрос на сделку.

    `sum` - сумма сделки _min: 100_

    **Returns**:

    Возвращает актуальную информацию о сделке.

    **Note**:

    После успешного выполнения, сделка перейдет в статус _'в ожидании'_

    """
    user_for = await UsersDAO.get_user(transaction.user_for)

    if transaction.user_for == user.id:
        raise TransactionUserError

    if user.balance < transaction.sum:
        raise TransactionExceedsBalance

    await TransactionDAO.create(
        initiator=user.id,
        user_for=transaction.user_for,
        sum=transaction.sum,
        status="в ожидании",
        creator=user.id,
    )

    send_user = user_for.chat_id
    if user_for.notification.create == True:
        try:
            await bot.send_message(
                send_user,
                text=f"⏳ У вас новая заявка на сделку с {user.first_name} | @{user.username}\nСумма: {transaction.sum}",
            )
        except TelegramBadRequest as e:
            extra = {
                "user_for": transaction.user_for,
                "sum": transaction.sum,
                "send_user": send_user
            }
            logger.error(msg="TelegramBadRequest", extra=extra, exc_info=True)
            raise TelegramError(e.message)
    raise TransactionCreated


@router.post("/canceled")
async def canceled(
    transaction: STransaction,
    user: SUser = Depends(get_current_user),
) -> SExceptionsINFO:
    """
    **Отменить сделку**

    **Headers**:

    Authorization: _access token_ *required

    **Args**:

    `transaction_id` - id отменяемой сделки.

    **Returns**:

    Возвращает актуальную информацию о сделке.

    **Note**:

    После успешного выполнения, сделка перейдет в статус _'отменено'_

    """
    current_transaction = await TransactionDAO.get_users(
        transaction_id=transaction.transaction_id
    )

    if not current_transaction:
        raise TransactionNotFound
    if user.id != current_transaction.initiator and user.id != current_transaction.user_for:
        raise TransactionErrorInitiatorOrUserFor
    if current_transaction.status == "отменено":
        raise TransactionStatusCanceled
    if current_transaction.status == "завершено":
        raise TransactionStatusСompleted
    if current_transaction.status == "активно":
        await TransactionDAO.canceled(
            user_id=user.id,
            transaction_id=transaction.transaction_id,
            status="отменено",
            chat_id_initiator=current_transaction.initiator_chat_id,
            chat_id_user_for=current_transaction.user_for_chat_id,
            balance=current_transaction.sum,
        )
        await TransactionDAO.update_rating(user_id=user.id)

        if str(user.id) == str(current_transaction.initiator) and current_transaction.notification_user_for_canceled == True:
            send_user = current_transaction.user_for_chat_id
            try:
                await bot.send_message(
                    send_user,
                    text=f"🚫 {user.first_name} | @{user.username} отменил активную сделку\n"
                    f"Сумма сделки составляла: {current_transaction.sum}р, средства были возвращены без учета комиссии"
                )
            except TelegramBadRequest as e:
                extra = {
                    "transaction_id": transaction.transaction_id
                }
                logger.error(msg="TelegramBadRequest", extra=extra, exc_info=True)
                raise TelegramError(e.message)
            raise TransactionStatusCanceledTrue
        
        if current_transaction.notification_initiator_canceled == True:
            send_user = current_transaction.initiator_chat_id
            try:
                await bot.send_message(
                    send_user,
                    text=f"🚫 {current_transaction.user_for_first_name} | @{current_transaction.user_for_username} отменил активную сделку\n"
                    f"Сумма сделки составляла: {current_transaction.sum}р, средства были возвращены без учета комиссии"
                )
            except TelegramBadRequest as e:
                extra = {
                    "transaction_id": transaction.transaction_id
                }
                logger.error(msg="TelegramBadRequest", extra=extra, exc_info=True)
                raise TelegramError(e.message)
            raise TransactionStatusCanceledTrue

    await TransactionDAO.update_status(
        transaction_id=transaction.transaction_id, status="отменено"
    )
    raise TransactionStatusCanceledTrue


@router.post("/accept")
async def accept(
    transaction: STransaction,
    user: SUser = Depends(get_current_user),
) -> SExceptionsINFO:
    """
    **Принять сделку**

    **Headers**:

    Authorization: _access token_ *required

    **Args**:

    `transaction_id` - id принимаемой сделки.

    **Returns**:

    Возвращает актуальную информацию о сделке.

    **Note**:

    После успешного выполнения, сделка перейдет в статус _'активно'_

    """
    current_transaction = await TransactionDAO.get_users(
        transaction_id=transaction.transaction_id
    )
    if not current_transaction:
        raise TransactionNotFound
    if user.id != current_transaction.initiator and user.id != current_transaction.user_for:
        raise TransactionErrorInitiatorOrUserFor
    if str(current_transaction.initiator) == str(user.id):
        raise TransactionErrorInitiator
    if current_transaction.status == "активно":
        raise TransactionStatusActive
    if current_transaction.status == "завершено":
        raise TransactionStatusСompleted
    if current_transaction.status == "отменено":
        raise TransactionStatusCanceled

    await TransactionDAO.accept(
        transaction_id=transaction.transaction_id,
        status="активно",
        chat_id_initiator=current_transaction.initiator_chat_id,
        chat_id_user_for=current_transaction.user_for_chat_id,
        balance=current_transaction.sum,
    )
    send_user = current_transaction.initiator_chat_id
    if current_transaction.notification_initiator_accept == True:
        try:
            await bot.send_message(
                send_user,
                text=f"✅ {current_transaction.user_for_first_name} | @{current_transaction.user_for_username} принял вашу заявку на сделку\nСумма: {current_transaction.sum}",
            )
        except TelegramBadRequest as e:
            extra = {
                "transaction_id": transaction.transaction_id
            }
            logger.error(msg="TelegramBadRequest", extra=extra, exc_info=True)
            raise TelegramError(e.message)
    raise TransactionStatusActiveTrue


@router.post("/conditions_are_met")
async def conditions_are_met(
    transaction: STransaction,
    user: SUser = Depends(get_current_user),
) -> SExceptionsINFO:
    """
    **Условия выполнены**

    **Headers**:

    Authorization: _access token_ *required

    **Args**:

    `transaction_id` - id подтверждаемой сделки.

    **Returns**:

    Возвращает актуальную информацию о сделке.

    **Note**:

    После успешного выполнения, сделка перейдет в статус _'завершена'_

    """
    current_transaction = await TransactionDAO.get_users(
        transaction_id=transaction.transaction_id
    )
    if not current_transaction:
        raise TransactionNotFound
    if user.id != current_transaction.initiator and user.id != current_transaction.user_for:
        raise TransactionErrorInitiatorOrUserFor
    if user.chat_id != current_transaction.initiator_chat_id:
        raise TransactionNotTheInitiator
    if current_transaction.status == "в ожидании":
        raise TransactionStatusPending
    if current_transaction.status == "завершено":
        raise TransactionStatusСompleted
    if current_transaction.status == "отменено":
        raise TransactionStatusCanceled
    update_transaction = await TransactionDAO.conditions_are_met(
        initiator=current_transaction.initiator,
        user_for=current_transaction.user_for,
        transaction_id=transaction.transaction_id,
        status="завершено",
        chat_id_initiator=current_transaction.initiator_chat_id,
        chat_id_user_for=current_transaction.user_for_chat_id,
        balance=current_transaction.sum,
    )
    commission = current_transaction.sum * Decimal((settings.COMMISION_PERCENTAGE / 100))
    commision_result = current_transaction.sum - commission
    send_user = current_transaction.user_for_chat_id
    if current_transaction.notification_user_for_conditions_are_met == True:
        try:
            await bot.send_message(
                send_user,
                text=f"⭐️ Сделка с {user.first_name} | @{user.username} была успешно завершена\n"
                f"Баланс пополнен на {round(commision_result, 2)}р с учетом комиссии {settings.COMMISION_PERCENTAGE}%"
            )
        except TelegramBadRequest as e:
            extra = {
                "transaction_id": transaction.transaction_id
            }
            logger.error(msg="TelegramBadRequest", extra=extra, exc_info=True)
            raise TelegramError(e.message)
    await TransactionDAO.update_rating(user_id=user.id)
    raise TransactionСonditionsAreMet


@router.get("/list_with_status")
async def list_with_status(
    user: SUser = Depends(get_current_user),
    statuses: Optional[str] = None,
) -> list[STransactionList] | SExceptionsINFO:
    """
    **Просмотр сделок**

    **Headers**:

    Authorization: _access token_ *required

    **Args**:

    `statuses` - статус фильтры, передаются через запятую (например: "в ожидании,завершено").
    - если не передать ни один статус, то вернутся все сделки пользователя без фильтра статуса.

    **Returns**:

    Возвращает все сделки с пользователями по статусу или без него.

    **Note**:

    Возможные статусы: _в ожидании_, _завершено_, _активно_, _отменено_.
    """
    if statuses is None:
        statuses = "в ожидании,отменено,активно,завершено"
    status_list = [status.strip() for status in statuses.split(",")]

    return await TransactionDAO.list_with_status(user_id=user.id, statuses=status_list)


# @router.get("/test/get_users/{transaction_id}")
# async def test_get_users(transaction_id: UUID):
#     return await TransactionDAO.get_users(transaction_id=transaction_id)

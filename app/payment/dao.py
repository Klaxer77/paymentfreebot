import uuid

from yookassa import Configuration, Payment, Payout

from app.config import settings
from app.dao.base import BaseDAO
from app.exceptions.base import ServerError
from app.payment.models import PaymentHistory
from app.logger import logger


class PaymentDAO(BaseDAO):
    model = PaymentHistory

    @staticmethod
    async def create(amount: str, metadata: dict):
        try:
            extra = dict(metadata)
            logger.debug(msg=f"amount: {amount}", extra=extra)
            Configuration.account_id = settings.YOOKASSA_SHOPID
            Configuration.secret_key = settings.YOOKASSA_SECRETKEY

            idempotence_key = str(uuid.uuid4())
            payment = Payment.create(
                {
                    "amount": {"value": amount, "currency": "RUB"},
                    "metadata": metadata,
                    "capture": True,
                    "confirmation": {
                        "type": "redirect",
                        "return_url": "https://t.me/paymentFreeDEV_bot",
                    },
                    "description": "Пополнение баланса",
                },
                idempotence_key,
            )
            return payment.confirmation.confirmation_url
        except Exception:
            extra = dict(metadata)
            logger.error(
                msg=f"Unknown Exc: cannot create payment, amount: {amount}",
                extra=extra,
                exc_info=True,
            )
            raise ServerError

    @staticmethod
    async def payout(amount: str, card_number: str, metadata: dict):
        try:
            extra = dict(metadata)
            logger.debug(msg=f"amount: {amount}, card_number: {card_number}", extra=extra)
            Configuration.account_id = settings.YOOKASSA_AGENTID
            Configuration.secret_key = settings.YOOKASSA_SECRETKEY_SHLUZ

            idempotence_key = str(uuid.uuid4())
            Payout.create(
                {
                    "amount": {"value": amount, "currency": "RUB"},
                    "payout_destination_data": {
                        "type": "bank_card",
                        "card": {"number": card_number},
                    },
                    "description": "Вывод средств",
                    "metadata": metadata,
                },
                idempotence_key,
            )
            return None
        except Exception:
            extra = dict(metadata)
            logger.error(
                msg=f"Unknown Exc: cannot payout payment, amount: {amount}, card_number: {card_number}",
                extra=extra,
                exc_info=True,
            )
            raise ServerError

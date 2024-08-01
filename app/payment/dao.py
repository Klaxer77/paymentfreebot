import uuid
from app.dao.base import BaseDAO
from yookassa import Payment, Configuration, Payout
from app.config import settings
from app.payment.models import PaymentHistory

class PaymentDAO(BaseDAO):
    model=PaymentHistory
    
    @staticmethod
    async def create(amount: str):
        Configuration.account_id = settings.YOOKASSA_SHOPID
        Configuration.secret_key = settings.YOOKASSA_SECRETKEY
        
        idempotence_key = str(uuid.uuid4())
        payment = Payment.create({
            "amount": {
                "value": amount,
                "currency": "RUB"
            },
            "metadata": {},
            "capture": True,
            "confirmation": {
                "type": "redirect",
                "return_url": "http://localhost:8000/"
            },
            "description": "Пополнение баланса"
        }, idempotence_key)
        return payment.confirmation.confirmation_url
    
    @staticmethod
    async def payout(amount: str, card_number: str):
        Configuration.account_id = settings.YOOKASSA_AGENTID
        Configuration.secret_key = settings.YOOKASSA_SECRETKEY_SHLUZ
        
        idempotence_key = str(uuid.uuid4())
        payment = Payout.create({
            "amount": {
            "value": amount,
            "currency": "RUB"
            },
            "payout_destination_data":
            {
                "type": "bank_card",
                "card": {
                "number": card_number
            }
            },
            "description": "Вывод средств",
            "metadata": {}
        }, idempotence_key)
        return None
    
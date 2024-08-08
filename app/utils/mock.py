import json
from datetime import datetime

from sqlalchemy import insert

from app.database import Base, async_session_maker, engine
from app.payment.models import PaymentHistory
from app.transaction.models import Transactions
from app.users.models import Users


async def mock_script():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", encoding="utf-8") as file:
            return json.load(file)

    users = open_mock_json("users")
    payment_history = open_mock_json("payment_history")
    transactions = open_mock_json("transactions")

    for payment in payment_history:
        payment["created_at"] = datetime.strptime(
            payment["created_at"], "%Y-%m-%d %H:%M:%S.%f"
        )
    for user in users:
        user["register_date"] = datetime.strptime(
            user["register_date"], "%Y-%m-%d %H:%M:%S.%f"
        )
    for transaction in transactions:
        transaction["created_at"] = datetime.strptime(
            transaction["created_at"], "%Y-%m-%d %H:%M:%S.%f"
        )
        if transaction["finished_at"] is not None:
            transaction["finished_at"] = datetime.strptime(
                transaction["finished_at"], "%Y-%m-%d %H:%M:%S.%f"
            )

    async with async_session_maker() as session:
        add_users = insert(Users).values(users)
        add_payment_history = insert(PaymentHistory).values(payment_history)
        add_transactions = insert(Transactions).values(transactions)

        await session.execute(add_users)
        await session.execute(add_payment_history)
        await session.execute(add_transactions)

        await session.commit()

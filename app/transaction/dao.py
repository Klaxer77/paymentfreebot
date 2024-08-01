from datetime import datetime
from decimal import Decimal
from uuid import UUID
from app.dao.base import BaseDAO
from app.transaction.models import Transactions
from app.database import async_session_maker
from sqlalchemy import insert, or_, select, and_, update
from sqlalchemy.orm import aliased
from app.database import engine
from app.users.models import Users


class TransactionDAO(BaseDAO):
    model = Transactions
    
    @staticmethod
    async def get_users(transaction_id: UUID):
        async with async_session_maker() as session:
            initiator_alias = aliased(Users)
            user_for_alias = aliased(Users)   

            query = select(
                Transactions.id, 
                Transactions.sum,
                Transactions.status,
                user_for_alias.chat_id.label('user_for_chat_id'), 
                user_for_alias.first_name.label('user_for_first_name'), 
                initiator_alias.chat_id.label('initiator_chat_id')).where(
                Transactions.id == transaction_id
            ).join(
                user_for_alias, Transactions.user_for == user_for_alias.id, isouter=True
            ).join(
                initiator_alias, Transactions.initiator == initiator_alias.id, isouter=True
            )
            
            result = await session.execute(query)
            return result.mappings().one()
        
    @staticmethod
    async def canceled(
        transaction_id: UUID, 
        status: str, 
        chat_id_initiator: int, 
        chat_id_user_for: int, 
        balance: Decimal):
        async with async_session_maker() as session:
            update_status_and_finished_date = (
                    update(Transactions).
                    where(Transactions.id == transaction_id).
                    values(finished_at=datetime.now(), status=status).
                    returning(Transactions)
                )
            update_balance_up = (
                    update(Users)
                    .where(Users.chat_id == chat_id_initiator)
                    .values(balance=Users.balance + Decimal(balance))
                )
            update_frozen_balance_down = (
                    update(Users)
                    .where(Users.chat_id == chat_id_user_for)
                    .values(frozen_balance=Users.frozen_balance - Decimal(balance))
                )
            await session.execute(update_status_and_finished_date)
            await session.execute(update_balance_up)
            await session.execute(update_frozen_balance_down)
            await session.commit()
                    
    @staticmethod
    async def accept(transaction_id: UUID, status: str, chat_id_initiator: int, chat_id_user_for: int, balance: Decimal):
        async with async_session_maker() as session:
            update_status = (
                    update(Transactions).
                    where(Transactions.id == transaction_id).
                    values(status=status).
                    returning(Transactions)
                )
            update_balance_down = (
                    update(Users)
                    .where(Users.chat_id == chat_id_initiator)
                    .values(balance=Users.balance - Decimal(balance))
                )
            update_frozen_balance_up = (
                    update(Users)
                    .where(Users.chat_id == chat_id_user_for)
                    .values(frozen_balance=Users.frozen_balance + Decimal(balance))
                )
            await session.execute(update_status)
            await session.execute(update_balance_down)
            await session.execute(update_frozen_balance_up)
            await session.commit()
    
    @classmethod
    async def update_status(cls, transaction_id: UUID, status: str):
        async with async_session_maker() as session:
            query = (
                update(cls.model).
                where(cls.model.id == transaction_id).
                values(finished_at=datetime.now(), status=status).
                returning(cls.model)
            )
            # print(query.compile(engine, compile_kwargs={"literal_binds": True}))
            result = await session.execute(query)
            await session.commit()
            return result.scalars().one()
    

    @classmethod
    async def add(cls, initiator, user_for, sum, status):
        async with async_session_maker() as session:
            query = insert(cls.model).values(initiator=initiator, user_for=user_for, sum=sum, status=status).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalar_one()
    
    @classmethod
    async def history_list(cls, initiator: UUID):
        async with async_session_maker() as session:
            query = select(
                Transactions.id,
                Transactions.sum,
                Transactions.status, 
                Transactions.created_at,
                Transactions.finished_at,
                Users.first_name, 
                Users.last_name, 
                Users.username, 
                Users.is_premium
                ).where(
                and_(
                    cls.model.initiator == initiator,
                    or_(
                        cls.model.status == "завершено",
                        cls.model.status == "отменено"
                    )
                )
            ).join(Users, cls.model.user_for == Users.id, isouter=True)
            result = await session.execute(query)
            return result.mappings().all()

    
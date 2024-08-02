from datetime import datetime
from decimal import Decimal
from uuid import UUID
import uuid
from app.dao.base import BaseDAO
from app.exceptions.transaction.exeptions import TransactionLimitBalance
from app.transaction.models import Transactions
from app.database import async_session_maker
from sqlalchemy import insert, or_, select, and_, update, func
from sqlalchemy.orm import aliased
from app.database import engine
from app.users.models import Users
import asyncpg

class TransactionDAO(BaseDAO):
    model = Transactions
    
    @staticmethod
    async def sum_transactions_for_user(initiator_id: UUID, status: str):
        async with async_session_maker() as session:
            query = select(func.sum(Transactions.sum).label("all_sum")).where(Transactions.initiator == initiator_id, Transactions.status == status)
            result = await session.execute(query)
            return result.scalars().one()
    
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
    async def conditions_are_met(
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
            update_frozen_balance_down = (
                    update(Users)
                    .where(Users.chat_id == chat_id_user_for)
                    .values(frozen_balance=Users.frozen_balance - Decimal(balance))
                )
            update_balance_up = (
                    update(Users)
                    .where(Users.chat_id == chat_id_user_for)
                    .values(balance=Users.balance + Decimal(balance))
                )
            await session.execute(update_status_and_finished_date)
            await session.execute(update_balance_up)
            await session.execute(update_frozen_balance_down)
            await session.commit()
        
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
            user_query = select(Users.balance).where(Users.id == initiator)
            all_sum = select(func.sum(Transactions.sum).label("all_sum")).where(
                Transactions.initiator == initiator, Transactions.status == status
            )
            
            result_user_query = await session.execute(user_query)
            current_balance = result_user_query.scalars().one()

            sum_transactions = await session.execute(all_sum)
            full_sum = sum_transactions.scalars().one() or Decimal(0.00)

            if full_sum + sum > current_balance:
                raise TransactionLimitBalance
            
            query = insert(cls.model).values(initiator=initiator, user_for=user_for, sum=sum, status=status).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            
            return result.scalar_one()
        
    @classmethod
    async def list_with_status(cls, user_id: UUID, status: str):
        async with async_session_maker() as session:
            get_initiator_query = select(Transactions.initiator).where(or_(Transactions.initiator == user_id, Transactions.user_for == user_id))
            result = await session.execute(get_initiator_query)
            initiator_id = result.scalars().all()
            if initiator_id[0] == user_id:
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
                        cls.model.initiator == user_id,
                        cls.model.status == status
                    )
                ).join(Users, cls.model.user_for == Users.id, isouter=True).order_by(Transactions.created_at.desc())
                    
            else:
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
                        cls.model.user_for == user_id,
                        cls.model.status == status
                    )
                ).join(Users, cls.model.initiator == Users.id, isouter=True).order_by(Transactions.created_at.desc())
            result = await session.execute(query)
            return result.mappings().all()

    
    @classmethod
    async def history_list(cls, user_id: UUID):
        async with async_session_maker() as session:
            get_initiator_query = select(Transactions.initiator).where(or_(Transactions.initiator == user_id, Transactions.user_for == user_id))
            result = await session.execute(get_initiator_query)
            initiator_id = result.scalars().all()
            if initiator_id[0] == user_id:
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
                ).join(
                    Users, cls.model.user_for == Users.id, isouter=True
                ).where(
                    and_(
                        cls.model.status.in_(["завершено", "отменено"]),
                        cls.model.initiator == user_id
                    )
                ).order_by(Transactions.created_at.desc())
            else:
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
                ).join(
                    Users, cls.model.initiator == Users.id, isouter=True
                ).where(
                    and_(
                        cls.model.status.in_(["завершено", "отменено"]),
                        cls.model.user_for == user_id
                    )
                ).order_by(Transactions.created_at.desc())

            result = await session.execute(query)
            return result.mappings().all()

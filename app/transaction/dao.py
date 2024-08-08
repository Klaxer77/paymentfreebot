from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, func, insert, or_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.exceptions.base import ServerError
from app.exceptions.transaction.exeptions import TransactionLimitBalance
from app.rating.models import Ratings
from app.rating.router import get_rating
from app.transaction.models import Transactions
from app.users.models import Users
from app.logger import logger
from app.database import engine
from app.config import settings


class TransactionDAO(BaseDAO):
    model = Transactions

    @staticmethod
    async def get_users(transaction_id: UUID):
        try:
            logger.debug(transaction_id)
            async with async_session_maker() as session:
                initiator_alias = aliased(Users)
                user_for_alias = aliased(Users)

                query = (
                    select(
                        Transactions.id,
                        Transactions.creator,
                        Transactions.sum,
                        Transactions.status,
                        Transactions.initiator,
                        Transactions.user_for,
                        user_for_alias.chat_id.label("user_for_chat_id"),
                        user_for_alias.first_name.label("user_for_first_name"),
                        initiator_alias.chat_id.label("initiator_chat_id"),
                    )
                    .where(Transactions.id == transaction_id)
                    .join(
                        user_for_alias,
                        Transactions.user_for == user_for_alias.id,
                        isouter=True,
                    )
                    .join(
                        initiator_alias,
                        Transactions.initiator == initiator_alias.id,
                        isouter=True,
                    )
                )
            logger.debug(query.compile(engine, compile_kwargs={"literal_binds": True}))
            result = await session.execute(query)
            return result.mappings().one_or_none()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot return users"
            extra = {"transaction_id": transaction_id}
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError

    @staticmethod
    async def conditions_are_met(
        initiator: UUID,
        user_for: UUID,
        transaction_id: UUID,
        status: str,
        chat_id_initiator: int,
        chat_id_user_for: int,
        balance: Decimal,
    ):
        try:
            commission = balance * Decimal((settings.COMMISION_PERCENTAGE / 100))
            logger.debug(
                user_for,
                initiator,
                transaction_id,
                status,
                chat_id_initiator,
                chat_id_user_for,
                balance)
            async with async_session_maker() as session:
                insert_rating_initiator = insert(Ratings).values(rated_user_id=initiator,score=5)
                insert_rating_user_for = insert(Ratings).values(rated_user_id=user_for,score=5)
                update_status_and_finished_date = (
                    update(Transactions)
                    .where(Transactions.id == transaction_id)
                    .values(finished_at=datetime.now(), status=status)
                    .returning(Transactions)
                )
                update_frozen_balance_down = (
                    update(Users)
                    .where(Users.chat_id == chat_id_user_for)
                    .values(frozen_balance=Users.frozen_balance - Decimal(balance))
                )
                update_balance_up = (
                    update(Users)
                    .where(Users.chat_id == chat_id_user_for)
                    .values(balance=Users.balance + Decimal(balance) - Decimal(commission))
                )
                await session.execute(update_status_and_finished_date)
                await session.execute(update_balance_up)
                await session.execute(update_frozen_balance_down)
                await session.execute(insert_rating_initiator)
                await session.execute(insert_rating_user_for)
                await session.commit()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": i can't meet the conditions for the transaction"
            extra = {
                "initiator": initiator,
                "user_for": user_for,
                "transaction_id": transaction_id,
                "status": status,
                "chat_id_initiator": chat_id_initiator,
                "chat_id_user_for": chat_id_user_for,
                "balance": balance,
            }
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError
        
    @staticmethod
    async def update_rating(user_id: UUID):
        async with async_session_maker() as session:
            rating = await get_rating(user_id=user_id)
            print(rating["rating"])
            update_rating_user = update(Users).where(Users.id==user_id).values(rating=rating["rating"])
            await session.execute(update_rating_user)
            await session.commit()

    @staticmethod
    async def canceled(
        user_id: UUID,
        transaction_id: UUID,
        status: str,
        chat_id_initiator: int,
        chat_id_user_for: int,
        balance: Decimal,
    ):
        try:
            logger.debug(
                user_id,
                transaction_id,
                status,
                chat_id_initiator,
                chat_id_user_for,
                balance)
            async with async_session_maker() as session:
                insert_rating = insert(Ratings).values(rated_user_id=user_id,score=4)
                update_status_and_finished_date = (
                    update(Transactions)
                    .where(Transactions.id == transaction_id)
                    .values(finished_at=datetime.now(), status=status)
                    .returning(Transactions)
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
                await session.execute(insert_rating)
                await session.commit()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot canceled transaction"
            extra = {
                "user_id": user_id,
                "transaction_id": transaction_id,
                "status": status,
                "chat_id_initiator": chat_id_initiator,
                "chat_id_user_for": chat_id_user_for,
                "balance": balance,
            }
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError

    @staticmethod
    async def accept(
        transaction_id: UUID,
        status: str,
        chat_id_initiator: int,
        chat_id_user_for: int,
        balance: Decimal,
    ):
        try:
            logger.debug(transaction_id,
                        status,
                        chat_id_initiator,
                        chat_id_user_for,
                        balance)
            async with async_session_maker() as session:
                update_status = (
                    update(Transactions)
                    .where(Transactions.id == transaction_id)
                    .values(status=status)
                    .returning(Transactions)
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

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot accept transaction"
            extra = {
                "transaction_id": transaction_id,
                "status": status,
                "chat_id_initiator": chat_id_initiator,
                "chat_id_user_for": chat_id_user_for,
                "balance": balance,
            }
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError

    @classmethod
    async def update_status(cls, transaction_id: UUID, status: str):
        try:
            logger.debug(transaction_id,status)
            async with async_session_maker() as session:
                query = (
                    update(cls.model)
                    .where(cls.model.id == transaction_id)
                    .values(finished_at=datetime.now(), status=status)
                    .returning(cls.model)
                )
                logger.debug(
                    query.compile(engine, compile_kwargs={"literal_binds": True})
                )
                result = await session.execute(query)
                await session.commit()
                return result.scalars().one()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot update status"
            extra = {"transaction_id": transaction_id, "status": status}
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError

    @classmethod
    async def create(
        cls, initiator: UUID, user_for: UUID, sum: Decimal, status: str, creator: UUID
    ):
        try:
            logger.debug(initiator,user_for,sum,status,creator)
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

                query = (
                    insert(cls.model)
                    .values(
                        initiator=initiator,
                        user_for=user_for,
                        sum=sum,
                        status=status,
                        creator=creator,
                    )
                    .returning(cls.model)
                )
                logger.debug(
                    query.compile(engine, compile_kwargs={"literal_binds": True})
                )
                result = await session.execute(query)
                await session.commit()
                return result.scalar_one()
        
        except TransactionLimitBalance as e:
            return {"detail": e.detail}

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot create transaction"
            extra = {
                "initiator": initiator,
                "user_for": user_for,
                "sum": sum,
                "status": status,
                "creator": creator,
            }
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError

    @classmethod
    async def list_with_status(cls, user_id: UUID, statuses: list):
        try:
            logger.debug(user_id,statuses)
            async with async_session_maker() as session:
                initiator_alias = aliased(Users)
                user_for_alias = aliased(Users)

                query = (
                    select(
                        Transactions.id,
                        Transactions.sum,
                        Transactions.status,
                        Transactions.created_at,
                        Transactions.finished_at,
                        Users.chat_id,
                        initiator_alias.first_name.label("initiator_first_name"),
                        initiator_alias.last_name.label("initiator_last_name"),
                        initiator_alias.username.label("initiator_username"),
                        initiator_alias.is_premium.label("initiator_is_premium"),
                        initiator_alias.chat_id.label("initiator_chat_id"),
                        user_for_alias.chat_id.label("user_for_chat_id"),
                        user_for_alias.first_name.label("user_for_first_name"),
                        user_for_alias.last_name.label("user_for_last_name"),
                        user_for_alias.username.label("user_for_username"),
                        user_for_alias.is_premium.label("user_for_is_premium"),
                    )
                    .join(
                        initiator_alias,
                        cls.model.initiator == initiator_alias.id,
                        isouter=True,
                    )
                    .join(
                        user_for_alias,
                        cls.model.user_for == user_for_alias.id,
                        isouter=True,
                    )
                    .join(Users, cls.model.creator == Users.id, isouter=True)
                    .where(
                        or_(
                            cls.model.initiator == user_id,
                            cls.model.user_for == user_id,
                        ),
                        and_(
                            cls.model.status.in_(statuses)
                        )
                    )
                    .order_by(Transactions.created_at.desc())
                )

                logger.debug(
                    query.compile(engine, compile_kwargs={"literal_binds": True})
                )

                result = await session.execute(query)
                transactions = result.mappings().all()

                formatted_results = [
                    {
                        "id": transaction.id,
                        "creator": {"chat_id": transaction.chat_id},
                        "sum": transaction.sum,
                        "status": transaction.status,
                        "created_at": transaction.created_at,
                        "finished_at": transaction.finished_at,
                        "initiator": {
                            "chat_id": transaction.initiator_chat_id,
                            "first_name": transaction.initiator_first_name,
                            "last_name": transaction.initiator_last_name,
                            "username": transaction.initiator_username,
                            "is_premium": transaction.initiator_is_premium,
                        },
                        "user_for": {
                            "chat_id": transaction.user_for_chat_id,
                            "first_name": transaction.user_for_first_name,
                            "last_name": transaction.user_for_last_name,
                            "username": transaction.user_for_username,
                            "is_premium": transaction.user_for_is_premium,
                        },
                    }
                    for transaction in transactions
                ]

                return formatted_results

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            if isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": cannot return transactions"
            extra = {"user_id": user_id, "statuses": statuses}
            logger.error(msg=msg, extra=extra, exc_info=True)
            raise ServerError

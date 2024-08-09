from uuid import UUID
from app.dao.base import BaseDAO
from app.notification.models import Notifications
from app.database import async_session_maker
from sqlalchemy import update
from app.database import engine

class NotificationDAO(BaseDAO):
    model = Notifications
    
    @classmethod
    async def update_notification(cls, user_id: UUID, action: bool):
        async with async_session_maker() as session:
            query = update(Notifications).where(Notifications.user_id==user_id).values(
                create=action,
                canceled=action,
                accept=action,
                conditions_are_met=action
                )
            await session.execute(query)
            await session.commit()
            
    @classmethod
    async def update_notification_one(cls, user_id: UUID, type_notification: str, action: bool):
        async with async_session_maker() as session:
            update_values = {type_notification: action}
            query = update(Notifications).where(Notifications.user_id == user_id).values(**update_values)
            await session.execute(query)
            await session.commit()
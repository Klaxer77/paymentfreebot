from sqlalchemy import Column, UUID, Boolean, ForeignKey, Integer
from app.database import Base


class Notifications(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    create = Column(Boolean, default=True, nullable=False)
    canceled = Column(Boolean, default=True, nullable=False)
    accept = Column(Boolean, default=True, nullable=False)
    conditions_are_met = Column(Boolean, default=True, nullable=False)
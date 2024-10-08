import uuid

from sqlalchemy import DECIMAL, Boolean, Column, DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(Integer, unique=True, nullable=False)
    rating = Column(Float, default=5, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=False)
    balance = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    frozen_balance = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    is_premium = Column(Boolean, nullable=True)
    register_date = Column(DateTime, nullable=False, default=func.current_timestamp())
    
    notification: Mapped["Notifications"] = relationship(back_populates="user")
    
    transaction_initiator: Mapped["Transactions"] = relationship(back_populates="user_initiator", foreign_keys="[Transactions.initiator]")
    transaction_user_for: Mapped["Transactions"] = relationship(back_populates="user_user_for", foreign_keys="[Transactions.user_for]")
    transaction_creator: Mapped["Transactions"] = relationship(back_populates="user_creator", foreign_keys="[Transactions.creator]")

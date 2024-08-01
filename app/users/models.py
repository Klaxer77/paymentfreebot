import uuid
from app.database import Base
from sqlalchemy import Column, Integer, String, Date , func, DateTime, Boolean, DECIMAL
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=False)
    balance = Column(DECIMAL(10,2), default=0.00, nullable=False)
    frozen_balance = Column(DECIMAL(10,2), default=0.00, nullable=False)
    is_premium = Column(Boolean, nullable=True)
    register_date = Column(DateTime, nullable=False, default=func.current_timestamp())
    
    payment_history = relationship("PaymentHistory", back_populates="user")
    
    
    
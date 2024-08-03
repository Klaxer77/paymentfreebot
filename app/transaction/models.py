from datetime import datetime
import uuid
from sqlalchemy import DECIMAL, UUID, Column, Boolean, DateTime, ForeignKey, String, func
from app.database import Base
from sqlalchemy.orm import relationship

class Transactions(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    initiator =  Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user_for = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    sum = Column(DECIMAL(10,2), nullable=False)
    created_at = Column(DateTime, default=datetime.now, server_default=func.now(), nullable=False)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(255), nullable=False)
    creator = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    


# class TransactionsHistory(Base):
#     __tablename__ = "transactions_history"
    
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     initiator =  Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
#     user_for = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
#     sum = Column(DECIMAL(10,2), nullable=False)
#     status = Column(String(255), nullable=False)
    
#     initiator = relationship("Users", back_populates="transactions_history")
#     user_for = relationship("Users", back_populates="transactions_history")


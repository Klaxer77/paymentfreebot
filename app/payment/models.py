from app.database import Base
from sqlalchemy import DECIMAL, UUID, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class PaymentHistory(Base):
    __tablename__ = "payment_history"
    
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id =  Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    amount = Column(DECIMAL(10,2), nullable=False)
    last4 = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    action = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)
    
    user = relationship("Users", back_populates="payment_history")
    
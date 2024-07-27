import uuid
from app.database import Base
from sqlalchemy import Column, Integer, String, Date , func, DateTime, Boolean
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy as sa

class Users(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(Integer, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=False)
    is_premium = Column(Boolean, nullable=True)
    register_date = Column(Date, nullable=False, default=func.current_date())
    
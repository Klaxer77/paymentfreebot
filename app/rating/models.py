from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column,Float, ForeignKey, Integer
from app.database import Base


class Ratings(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rated_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)
    

import uuid
from datetime import datetime

from sqlalchemy import (
    DECIMAL,
    UUID,
    Column,
    DateTime,
    ForeignKey,
    String,
    func,
)

from app.database import Base


class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    initiator = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_for = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    sum = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(
        DateTime, default=datetime.now, server_default=func.now(), nullable=False
    )
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(255), nullable=False)
    creator = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

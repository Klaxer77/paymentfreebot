import uuid
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped

from sqlalchemy import (
    DECIMAL,
    UUID,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    func,
)

from app.database import Base


class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    initiator = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user_for = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sum = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(
        DateTime, default=datetime.now, server_default=func.now(), nullable=False
    )
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(255), nullable=False)
    creator = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    user_initiator: Mapped["Users"] = relationship(back_populates="transaction_initiator", foreign_keys=[initiator])
    user_user_for: Mapped["Users"] = relationship(back_populates="transaction_user_for", foreign_keys=[user_for])
    user_creator: Mapped["Users"] = relationship(back_populates="transaction_creator", foreign_keys=[creator])
    

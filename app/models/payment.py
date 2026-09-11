from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Index
)
from sqlalchemy.orm import relationship

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey(
            "orders.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    amount = Column(
        Float,
        nullable=False
    )

    payment_method = Column(
        String(20),
        nullable=False
    )

    transaction_id = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True
    )

    payment_status = Column(
        String(20),
        default="PENDING",
        nullable=False,
        index=True
    )

    paid_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    order = relationship(
        "Order",
        backref="payment"
    )

    __table_args__ = (
        Index(
            "ix_payments_order_status",
            "order_id",
            "payment_status"
        ),
    )
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    Index
)
from sqlalchemy.orm import relationship

from app.database import Base


class Refund(Base):
    __tablename__ = "refunds"

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

    payment_id = Column(
        Integer,
        ForeignKey(
            "payments.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    refund_amount = Column(
        Float,
        nullable=False
    )

    reason = Column(
        String(500),
        nullable=True
    )

    refund_status = Column(
        String(20),
        default="PENDING",
        nullable=False,
        index=True
    )

    refund_transaction_id = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    processed_at = Column(
        DateTime,
        nullable=True
    )

    order = relationship(
        "Order",
        backref="refunds"
    )

    payment = relationship(
        "Payment",
        backref="refunds"
    )

    __table_args__ = (
        Index(
            "ix_refunds_order_status",
            "order_id",
            "refund_status"
        ),
    )
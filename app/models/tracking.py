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


class OrderTracking(Base):
    __tablename__ = "order_tracking"

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

    status = Column(
        String(30),
        nullable=False,
        index=True
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    remarks = Column(
        String(500),
        nullable=True
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    order = relationship(
        "Order",
        backref="tracking_history"
    )

    __table_args__ = (
        Index(
            "ix_order_tracking_order_timestamp",
            "order_id",
            "timestamp"
        ),
    )
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    Index
)
from sqlalchemy.orm import relationship

from app.database import Base


class DeliveryPartner(Base):
    __tablename__ = "delivery_partners"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    phone = Column(
        String(20),
        nullable=False
    )

    vehicle_type = Column(
        String(50),
        nullable=False
    )

    vehicle_number = Column(
        String(50),
        nullable=False,
        unique=True
    )

    availability_status = Column(
        String(30),
        nullable=False,
        default="AVAILABLE",
        index=True
    )

    current_latitude = Column(
        Float,
        nullable=True
    )

    current_longitude = Column(
        Float,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
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

    user = relationship("User")

    __table_args__ = (
        Index(
            "ix_delivery_partner_availability",
            "availability_status",
            "is_active"
        ),
    )
from datetime import time

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Time,
)

from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)

    restaurant_name = Column(
        String(150),
        nullable=False,
        index=True
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    address = Column(
        String(255),
        nullable=False
    )

    city = Column(
        String(100),
        nullable=False,
        index=True
    )

    phone = Column(
        String(20),
        nullable=False
    )

    cuisine_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    opening_time = Column(
        Time,
        nullable=False
    )

    closing_time = Column(
        Time,
        nullable=False
    )

    status = Column(
        String(40),
        nullable=False,
        default="OPEN",
        index=True
    )

    delivery_radius = Column(
        Float,
        nullable=False
    )

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False
    )
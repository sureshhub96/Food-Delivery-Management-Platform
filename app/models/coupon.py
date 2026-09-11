from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean
)

from app.database import Base


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)

    coupon_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    discount_type = Column(
        String(20),
        nullable=False
    )
    # PERCENTAGE / FIXED

    discount_value = Column(
        Float,
        nullable=False
    )

    min_order_amount = Column(
        Float,
        default=0.0,
        nullable=False
    )

    max_discount = Column(
        Float,
        nullable=True
    )

    start_date = Column(
        DateTime,
        nullable=False
    )

    end_date = Column(
        DateTime,
        nullable=False
    )

    usage_limit = Column(
        Integer,
        nullable=True
    )

    used_count = Column(
        Integer,
        default=0,
        nullable=False
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
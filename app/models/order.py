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


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )

    address_id = Column(
        Integer,
        ForeignKey("addresses.id"),
        nullable=False
    )

    subtotal = Column(
        Float,
        nullable=False
    )

    delivery_fee = Column(
        Float,
        nullable=False,
        default=0.0
    )

    discount = Column(
        Float,
        nullable=False,
        default=0.0
    )

    tax = Column(
        Float,
        nullable=False,
        default=0.0
    )

    total_amount = Column(
        Float,
        nullable=False
    )

    order_status = Column(
        String(30),
        nullable=False,
        default="PENDING",
        index=True
    )

    payment_status = Column(
        String(30),
        nullable=False,
        default="PENDING",
        index=True
    )

    coupon_code = Column(
        String(50),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    customer = relationship("Customer")

    restaurant = relationship("Restaurant")

    address = relationship("Address")

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "ix_orders_customer_status",
            "customer_id",
            "order_status"
        ),
        Index(
            "ix_orders_restaurant_date",
            "restaurant_id",
            "created_at"
        ),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

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

    food_item_id = Column(
        Integer,
        ForeignKey("food_items.id"),
        nullable=False
    )

    food_name = Column(
        String(200),
        nullable=False
    )

    price = Column(
        Float,
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    item_total = Column(
        Float,
        nullable=False
    )

    order = relationship(
        "Order",
        back_populates="items"
    )

    food_item = relationship("FoodItem")

    delivery_partner_id = Column(
    Integer,
    ForeignKey("delivery_partners.id"),
    nullable=True,
    index=True
)

delivery_partner = relationship(
    "DeliveryPartner"
)
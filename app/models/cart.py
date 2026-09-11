from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=True,
        index=True
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    customer = relationship("Customer", backref="cart")

    restaurant = relationship("Restaurant")

    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan"
    )


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)

    cart_id = Column(
        Integer,
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    food_item_id = Column(
        Integer,
        ForeignKey("food_items.id"),
        nullable=False,
        index=True
    )

    quantity = Column(Integer, nullable=False)

    cart = relationship(
        "Cart",
        back_populates="items"
    )

    food_item = relationship("FoodItem")
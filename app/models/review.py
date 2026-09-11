from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index
)
from sqlalchemy.orm import relationship

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey(
            "customers.id",
            ondelete="CASCADE"
        ),
        nullable=False,
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

    restaurant_id = Column(
        Integer,
        ForeignKey(
            "restaurants.id",
            ondelete="CASCADE"
        ),
        nullable=True,
        index=True
    )

    food_item_id = Column(
        Integer,
        ForeignKey(
            "food_items.id",
            ondelete="CASCADE"
        ),
        nullable=True,
        index=True
    )

    delivery_partner_id = Column(
        Integer,
        ForeignKey(
            "delivery_partners.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    rating = Column(
        Integer,
        nullable=False
    )

    review = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    customer = relationship(
        "Customer",
        backref="reviews"
    )

    order = relationship(
        "Order",
        backref="reviews"
    )

    restaurant = relationship(
        "Restaurant",
        backref="reviews"
    )

    food_item = relationship(
        "FoodItem",
        backref="reviews"
    )

    delivery_partner = relationship(
        "DeliveryPartner",
        backref="reviews"
    )

    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="check_review_rating"
        ),
        Index(
            "ix_reviews_restaurant_rating",
            "restaurant_id",
            "rating"
        ),
        Index(
            "ix_reviews_food_rating",
            "food_item_id",
            "rating"
        ),
        Index(
            "ix_reviews_delivery_rating",
            "delivery_partner_id",
            "rating"
        ),
    )
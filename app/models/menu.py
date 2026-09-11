from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from app.database import Base


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )

    category = Column(
        String(100),
        nullable=False,
        index=True
    )

    name = Column(
        String(150),
        nullable=False,
        index=True
    )

    description = Column(
        Text,
        nullable=True
    )

    price = Column(
        Float,
        nullable=False
    )

    preparation_time = Column(
        Integer,
        nullable=False
    )

    availability = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    vegetarian = Column(
        Boolean,
        default=False,
        nullable=False
    )

    spicy_level = Column(
        Integer,
        default=0,
        nullable=False
    )

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False
    )
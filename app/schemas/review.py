from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    field_validator
)


class ReviewCreate(BaseModel):

    order_id: int = Field(gt=0)

    restaurant_id: Optional[int] = Field(
        default=None,
        gt=0
    )

    food_item_id: Optional[int] = Field(
        default=None,
        gt=0
    )

    delivery_partner_id: Optional[int] = Field(
        default=None,
        gt=0
    )

    rating: int = Field(
        ge=1,
        le=5
    )

    review: Optional[str] = Field(
        default=None,
        max_length=1000
    )

    @field_validator("review")
    @classmethod
    def clean_review(cls, value):
        if value is not None:
            value = value.strip()

            if not value:
                return None

        return value


class ReviewResponse(BaseModel):

    id: int
    customer_id: int
    order_id: int

    restaurant_id: Optional[int]
    food_item_id: Optional[int]
    delivery_partner_id: Optional[int]

    rating: int
    review: Optional[str]

    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
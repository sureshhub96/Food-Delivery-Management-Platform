from datetime import time
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, field_validator


# =========================================================
# CREATE RESTAURANT
# =========================================================

class RestaurantCreate(BaseModel):
    restaurant_name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    address: str = Field(
        ...,
        min_length=5,
        max_length=255
    )

    city: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    phone: str | None = Field(
        default=None,
        max_length=15
    )

    cuisine_type: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    opening_time: time
    closing_time: time

    status: str = Field(
        default="OPEN"
    )

    delivery_radius: Decimal = Field(
        default=5,
        gt=0
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        value = value.upper()

        allowed_statuses = {
            "OPEN",
            "CLOSED",
            "BUSY",
            "TEMPORARILY_UNAVAILABLE"
        }

        if value not in allowed_statuses:
            raise ValueError(
                "Status must be OPEN, CLOSED, BUSY, "
                "or TEMPORARILY_UNAVAILABLE"
            )

        return value


# =========================================================
# UPDATE RESTAURANT
# =========================================================

class RestaurantUpdate(BaseModel):
    restaurant_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    address: str | None = Field(
        default=None,
        min_length=5,
        max_length=255
    )

    city: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    phone: str | None = Field(
        default=None,
        max_length=15
    )

    cuisine_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    opening_time: time | None = None

    closing_time: time | None = None

    status: str | None = None

    delivery_radius: Decimal | None = Field(
        default=None,
        gt=0
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.upper()

        allowed_statuses = {
            "OPEN",
            "CLOSED",
            "BUSY",
            "TEMPORARILY_UNAVAILABLE"
        }

        if value not in allowed_statuses:
            raise ValueError(
                "Status must be OPEN, CLOSED, BUSY, "
                "or TEMPORARILY_UNAVAILABLE"
            )

        return value


# =========================================================
# RESTAURANT RESPONSE
# =========================================================

class RestaurantResponse(BaseModel):
    id: int
    restaurant_name: str
    owner_id: int

    address: str
    city: str

    phone: str | None = None

    cuisine_type: str

    opening_time: time
    closing_time: time

    status: str

    delivery_radius: Decimal

    is_deleted: bool

    model_config = ConfigDict(
        from_attributes=True
    )
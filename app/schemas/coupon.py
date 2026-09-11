from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CouponCreate(BaseModel):
    coupon_code: str = Field(
        min_length=3,
        max_length=50
    )

    discount_type: str

    discount_value: float = Field(gt=0)

    min_order_amount: float = Field(
        default=0.0,
        ge=0
    )

    max_discount: Optional[float] = Field(
        default=None,
        gt=0
    )

    start_date: datetime

    end_date: datetime

    usage_limit: Optional[int] = Field(
        default=None,
        gt=0
    )

    is_active: bool = True

    @field_validator("coupon_code")
    @classmethod
    def validate_coupon_code(cls, value):
        return value.strip().upper()

    @field_validator("discount_type")
    @classmethod
    def validate_discount_type(cls, value):
        value = value.upper()

        if value not in ["PERCENTAGE", "FIXED"]:
            raise ValueError(
                "discount_type must be PERCENTAGE or FIXED"
            )

        return value

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, value, info):
        start_date = info.data.get("start_date")

        if start_date and value <= start_date:
            raise ValueError(
                "end_date must be after start_date"
            )

        return value


class CouponUpdate(BaseModel):
    discount_type: Optional[str] = None

    discount_value: Optional[float] = Field(
        default=None,
        gt=0
    )

    min_order_amount: Optional[float] = Field(
        default=None,
        ge=0
    )

    max_discount: Optional[float] = Field(
        default=None,
        gt=0
    )

    start_date: Optional[datetime] = None

    end_date: Optional[datetime] = None

    usage_limit: Optional[int] = Field(
        default=None,
        gt=0
    )

    is_active: Optional[bool] = None


class CouponResponse(BaseModel):
    id: int
    coupon_code: str
    discount_type: str
    discount_value: float
    min_order_amount: float
    max_discount: Optional[float]
    start_date: datetime
    end_date: datetime
    usage_limit: Optional[int]
    used_count: int
    is_active: bool

    class Config:
        from_attributes = True


class CouponApplyRequest(BaseModel):
    coupon_code: str
    order_amount: float = Field(gt=0)

    @field_validator("coupon_code")
    @classmethod
    def normalize_code(cls, value):
        return value.strip().upper()


class CouponApplyResponse(BaseModel):
    coupon_code: str
    order_amount: float
    discount_amount: float
    final_amount: float
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


VALID_PAYMENT_METHODS = {
    "UPI",
    "CARD",
    "WALLET",
    "COD",
}

VALID_PAYMENT_STATUSES = {
    "PENDING",
    "SUCCESS",
    "FAILED",
    "REFUNDED",
}


class PaymentCreate(BaseModel):
    order_id: int = Field(gt=0)
    amount: float = Field(gt=0)
    payment_method: str
    transaction_id: Optional[str] = Field(
        default=None,
        max_length=100
    )

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, value: str):
        value = value.upper()

        if value not in VALID_PAYMENT_METHODS:
            raise ValueError(
                "Payment method must be UPI, CARD, WALLET or COD"
            )

        return value

    @field_validator("transaction_id")
    @classmethod
    def validate_transaction_id(cls, value):
        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError(
                    "Transaction ID cannot be empty"
                )

        return value


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    payment_method: str
    transaction_id: Optional[str]
    payment_status: str
    paid_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
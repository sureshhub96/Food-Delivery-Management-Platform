from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RefundCreate(BaseModel):
    order_id: int = Field(gt=0)

    reason: Optional[str] = Field(
        default=None,
        max_length=500
    )


class RefundResponse(BaseModel):
    id: int
    order_id: int
    payment_id: Optional[int]
    refund_amount: float
    reason: Optional[str]
    refund_status: str
    refund_transaction_id: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True
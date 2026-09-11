from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    address_id: int

    coupon_code: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: int
    food_item_id: int
    food_name: str
    price: float
    quantity: int
    item_total: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    address_id: int

    subtotal: float
    delivery_fee: float
    discount: float
    tax: float
    total_amount: float

    order_status: str
    payment_status: str

    coupon_code: Optional[str]

    created_at: datetime

    items: list[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    order_status: str


class OrderCancelRequest(BaseModel):
    reason: Optional[str] = None
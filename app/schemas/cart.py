from pydantic import BaseModel, Field
from typing import List


class CartItemCreate(BaseModel):
    food_item_id: int
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    id: int
    food_item_id: int
    food_name: str
    price: float
    quantity: int
    item_total: float

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int | None
    items: List[CartItemResponse]
    subtotal: float
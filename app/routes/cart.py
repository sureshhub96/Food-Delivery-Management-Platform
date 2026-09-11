from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse
)
from app.services.cart_service import CartService
from app.utils.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)

cart_service = CartService()


@router.post("/items")
def add_to_cart(
    request: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = cart_service.add_item(
        db,
        current_user,
        request.food_item_id,
        request.quantity
    )

    return {
        "message": "Item added to cart successfully",
        "cart_item_id": item.id,
        "quantity": item.quantity
    }


@router.get("", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = cart_service.get_cart(
        db,
        current_user
    )

    items = []

    for item in cart.items:
        items.append({
            "id": item.id,
            "food_item_id": item.food_item_id,
            "food_name": item.food_item.name,
            "price": float(item.food_item.price),
            "quantity": item.quantity,
            "item_total": round(
                float(item.food_item.price) * item.quantity,
                2
            )
        })

    subtotal = cart_service.calculate_subtotal(cart)

    return {
        "id": cart.id,
        "customer_id": cart.customer_id,
        "restaurant_id": cart.restaurant_id,
        "items": items,
        "subtotal": subtotal
    }


@router.put("/items/{item_id}")
def update_cart_item(
    item_id: int,
    request: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = cart_service.update_item(
        db,
        current_user,
        item_id,
        request.quantity
    )

    return {
        "message": "Cart item updated successfully",
        "cart_item_id": item.id,
        "quantity": item.quantity
    }


@router.delete("/items/{item_id}")
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return cart_service.remove_item(
        db,
        current_user,
        item_id
    )


@router.delete("/clear")
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return cart_service.clear_cart(
        db,
        current_user
    )
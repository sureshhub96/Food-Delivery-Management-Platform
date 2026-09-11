from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderResponse
)
from app.services.order_service import OrderService
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

order_service = OrderService()


# ==================================================
# CREATE ORDER
# ==================================================

@router.post(
    "",
    response_model=OrderResponse
)
def create_order(
    request: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return order_service.create_order(
        db=db,
        current_user=current_user,
        address_id=request.address_id,
        coupon_code=request.coupon_code
    )


# ==================================================
# GET MY ORDERS
# ==================================================

@router.get(
    "",
    response_model=list[OrderResponse]
)
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return order_service.get_my_orders(
        db=db,
        current_user=current_user
    )


# ==================================================
# SEARCH ORDERS
# ==================================================

@router.get(
    "/search"
)
def search_orders(
    restaurant_id: int | None = Query(
        default=None
    ),
    order_status: str | None = Query(
        default=None
    ),
    payment_status: str | None = Query(
        default=None
    ),
    start_date: datetime | None = Query(
        default=None
    ),
    end_date: datetime | None = Query(
        default=None
    ),
    page: int = Query(
        default=1,
        ge=1
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    sort_order: str = Query(
        default="desc"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return order_service.search_orders(
        db=db,
        current_user=current_user,
        restaurant_id=restaurant_id,
        order_status=order_status,
        payment_status=payment_status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit,
        sort_order=sort_order
    )


# ==================================================
# GET SINGLE ORDER
# ==================================================

@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return order_service.get_order(
        db=db,
        current_user=current_user,
        order_id=order_id
    )


# ==================================================
# CANCEL ORDER
# ==================================================

@router.put(
    "/{order_id}/cancel",
    response_model=OrderResponse
)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return order_service.cancel_order(
        db=db,
        current_user=current_user,
        order_id=order_id
    )
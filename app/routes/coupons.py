from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user import User

from app.schemas.coupon import (
    CouponCreate,
    CouponUpdate,
    CouponResponse,
    CouponApplyRequest,
    CouponApplyResponse
)

from app.services.coupon_service import CouponService

from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/coupons",
    tags=["Coupons"]
)

coupon_service = CouponService()


@router.post(
    "",
    response_model=CouponResponse
)
def create_coupon(
    request: CouponCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return coupon_service.create_coupon(
        db,
        request,
        current_user
    )


@router.get(
    "",
    response_model=list[CouponResponse]
)
def get_coupons(
    db: Session = Depends(get_db)
):
    return coupon_service.get_all_coupons(db)


@router.get(
    "/{coupon_id}",
    response_model=CouponResponse
)
def get_coupon(
    coupon_id: int,
    db: Session = Depends(get_db)
):
    return coupon_service.get_coupon(
        db,
        coupon_id
    )


@router.put(
    "/{coupon_id}",
    response_model=CouponResponse
)
def update_coupon(
    coupon_id: int,
    request: CouponUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return coupon_service.update_coupon(
        db,
        coupon_id,
        request,
        current_user
    )


@router.delete("/{coupon_id}")
def delete_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return coupon_service.delete_coupon(
        db,
        coupon_id,
        current_user
    )


@router.post(
    "/apply",
    response_model=CouponApplyResponse
)
def apply_coupon(
    request: CouponApplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return coupon_service.validate_coupon(
        db,
        request.coupon_code,
        request.order_amount
    )
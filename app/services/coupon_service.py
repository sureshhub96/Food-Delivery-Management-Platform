from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.coupon import Coupon
from app.models.user import User

from app.repositories.coupon_repository import CouponRepository


class CouponService:

    def __init__(self):
        self.repository = CouponRepository()

    def create_coupon(
        self,
        db: Session,
        data,
        current_user: User
    ):
        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="Only admin can create coupons"
            )

        existing = self.repository.get_by_code(
            db,
            data.coupon_code
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Coupon code already exists"
            )

        if (
            data.discount_type == "PERCENTAGE"
            and data.discount_value > 100
        ):
            raise HTTPException(
                status_code=400,
                detail="Percentage discount cannot exceed 100"
            )

        coupon = Coupon(
            coupon_code=data.coupon_code.upper(),
            discount_type=data.discount_type,
            discount_value=data.discount_value,
            min_order_amount=data.min_order_amount,
            max_discount=data.max_discount,
            start_date=data.start_date,
            end_date=data.end_date,
            usage_limit=data.usage_limit,
            is_active=data.is_active
        )

        return self.repository.create(
            db,
            coupon
        )

    def get_coupon(
        self,
        db: Session,
        coupon_id: int
    ):
        coupon = self.repository.get_by_id(
            db,
            coupon_id
        )

        if not coupon:
            raise HTTPException(
                status_code=404,
                detail="Coupon not found"
            )

        return coupon

    def get_all_coupons(
        self,
        db: Session
    ):
        return self.repository.get_all(db)

    def update_coupon(
        self,
        db: Session,
        coupon_id: int,
        data,
        current_user: User
    ):
        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="Only admin can update coupons"
            )

        coupon = self.get_coupon(
            db,
            coupon_id
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "discount_type" in update_data:
            discount_type = update_data["discount_type"].upper()

            if discount_type not in [
                "PERCENTAGE",
                "FIXED"
            ]:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid discount type"
                )

            update_data["discount_type"] = discount_type

        discount_type = update_data.get(
            "discount_type",
            coupon.discount_type
        )

        discount_value = update_data.get(
            "discount_value",
            coupon.discount_value
        )

        if (
            discount_type == "PERCENTAGE"
            and discount_value > 100
        ):
            raise HTTPException(
                status_code=400,
                detail="Percentage discount cannot exceed 100"
            )

        start_date = update_data.get(
            "start_date",
            coupon.start_date
        )

        end_date = update_data.get(
            "end_date",
            coupon.end_date
        )

        if end_date <= start_date:
            raise HTTPException(
                status_code=400,
                detail="end_date must be after start_date"
            )

        for field, value in update_data.items():
            setattr(coupon, field, value)

        return self.repository.update(
            db,
            coupon
        )

    def delete_coupon(
        self,
        db: Session,
        coupon_id: int,
        current_user: User
    ):
        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="Only admin can delete coupons"
            )

        coupon = self.get_coupon(
            db,
            coupon_id
        )

        self.repository.delete(
            db,
            coupon
        )

        return {
            "message": "Coupon deleted successfully"
        }

    def validate_coupon(
        self,
        db: Session,
        coupon_code: str,
        order_amount: float
    ):
        coupon = self.repository.get_by_code(
            db,
            coupon_code
        )

        if not coupon:
            raise HTTPException(
                status_code=404,
                detail="Invalid coupon code"
            )

        now = datetime.utcnow()

        if not coupon.is_active:
            raise HTTPException(
                status_code=400,
                detail="Coupon is inactive"
            )

        if now < coupon.start_date:
            raise HTTPException(
                status_code=400,
                detail="Coupon is not active yet"
            )

        if now > coupon.end_date:
            raise HTTPException(
                status_code=400,
                detail="Coupon has expired"
            )

        if (
            coupon.usage_limit is not None
            and coupon.used_count >= coupon.usage_limit
        ):
            raise HTTPException(
                status_code=400,
                detail="Coupon usage limit exceeded"
            )

        if order_amount < coupon.min_order_amount:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Minimum order amount is "
                    f"{coupon.min_order_amount}"
                )
            )

        discount = self.calculate_discount(
            coupon,
            order_amount
        )

        final_amount = max(
            order_amount - discount,
            0
        )

        return {
            "coupon_code": coupon.coupon_code,
            "order_amount": round(order_amount, 2),
            "discount_amount": round(discount, 2),
            "final_amount": round(final_amount, 2)
        }

    def calculate_discount(
        self,
        coupon: Coupon,
        order_amount: float
    ):
        if coupon.discount_type == "PERCENTAGE":

            discount = (
                order_amount
                * coupon.discount_value
                / 100
            )

        else:
            discount = coupon.discount_value

        if coupon.max_discount is not None:
            discount = min(
                discount,
                coupon.max_discount
            )

        discount = min(
            discount,
            order_amount
        )

        return round(discount, 2)
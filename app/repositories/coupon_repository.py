from sqlalchemy.orm import Session

from app.models.coupon import Coupon


class CouponRepository:

    def create(
        self,
        db: Session,
        coupon: Coupon
    ):
        db.add(coupon)
        db.commit()
        db.refresh(coupon)

        return coupon

    def get_by_id(
        self,
        db: Session,
        coupon_id: int
    ):
        return (
            db.query(Coupon)
            .filter(Coupon.id == coupon_id)
            .first()
        )

    def get_by_code(
        self,
        db: Session,
        coupon_code: str
    ):
        return (
            db.query(Coupon)
            .filter(
                Coupon.coupon_code == coupon_code.upper()
            )
            .first()
        )

    def get_all(
        self,
        db: Session
    ):
        return (
            db.query(Coupon)
            .order_by(Coupon.created_at.desc())
            .all()
        )

    def update(
        self,
        db: Session,
        coupon: Coupon
    ):
        db.commit()
        db.refresh(coupon)

        return coupon

    def delete(
        self,
        db: Session,
        coupon: Coupon
    ):
        db.delete(coupon)
        db.commit()
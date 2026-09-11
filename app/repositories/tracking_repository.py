from sqlalchemy.orm import Session

from app.models.tracking import OrderTracking


class TrackingRepository:

    def create(
        self,
        db: Session,
        tracking: OrderTracking
    ):
        db.add(tracking)
        db.commit()
        db.refresh(tracking)

        return tracking

    def get_by_id(
        self,
        db: Session,
        tracking_id: int
    ):
        return (
            db.query(OrderTracking)
            .filter(
                OrderTracking.id == tracking_id
            )
            .first()
        )

    def get_order_tracking(
        self,
        db: Session,
        order_id: int
    ):
        return (
            db.query(OrderTracking)
            .filter(
                OrderTracking.order_id == order_id
            )
            .order_by(
                OrderTracking.timestamp.asc()
            )
            .all()
        )

    def get_latest_tracking(
        self,
        db: Session,
        order_id: int
    ):
        return (
            db.query(OrderTracking)
            .filter(
                OrderTracking.order_id == order_id
            )
            .order_by(
                OrderTracking.timestamp.desc()
            )
            .first()
        )
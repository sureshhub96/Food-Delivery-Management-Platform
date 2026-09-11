from sqlalchemy.orm import Session

from app.models.delivery import DeliveryPartner
from app.models.order import Order


class DeliveryRepository:

    def create(
        self,
        db: Session,
        partner: DeliveryPartner
    ):
        db.add(partner)
        db.commit()
        db.refresh(partner)

        return partner

    def get_by_id(
        self,
        db: Session,
        partner_id: int
    ):
        return (
            db.query(DeliveryPartner)
            .filter(
                DeliveryPartner.id == partner_id
            )
            .first()
        )

    def get_by_user_id(
        self,
        db: Session,
        user_id: int
    ):
        return (
            db.query(DeliveryPartner)
            .filter(
                DeliveryPartner.user_id == user_id
            )
            .first()
        )

    def get_by_vehicle_number(
        self,
        db: Session,
        vehicle_number: str
    ):
        return (
            db.query(DeliveryPartner)
            .filter(
                DeliveryPartner.vehicle_number
                == vehicle_number
            )
            .first()
        )

    def get_all(
        self,
        db: Session
    ):
        return (
            db.query(DeliveryPartner)
            .order_by(
                DeliveryPartner.created_at.desc()
            )
            .all()
        )

    def get_active_order(
        self,
        db: Session,
        partner_id: int
    ):
        active_statuses = [
            "PENDING",
            "ACCEPTED",
            "PREPARING",
            "READY",
            "PICKED_UP",
            "OUT_FOR_DELIVERY"
        ]

        return (
            db.query(Order)
            .filter(
                Order.delivery_partner_id
                == partner_id,
                Order.order_status.in_(
                    active_statuses
                )
            )
            .first()
        )

    def update(
        self,
        db: Session,
        partner: DeliveryPartner
    ):
        db.commit()
        db.refresh(partner)

        return partner
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order import Order
from app.models.delivery import DeliveryPartner

from app.repositories.delivery_repository import (
    DeliveryRepository
)


class DeliveryService:

    VALID_STATUSES = [
        "AVAILABLE",
        "BUSY",
        "OFFLINE"
    ]

    ACTIVE_ORDER_STATUSES = [
        "PENDING",
        "ACCEPTED",
        "PREPARING",
        "READY",
        "PICKED_UP",
        "OUT_FOR_DELIVERY"
    ]

    def __init__(self):
        self.repository = DeliveryRepository()

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------

    def create_partner(
        self,
        db: Session,
        data,
        current_user: User
    ):
        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="Only admin can create delivery partners"
            )

        user = (
            db.query(User)
            .filter(User.id == data.user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        if user.role != "DELIVERY_PARTNER":
            raise HTTPException(
                status_code=400,
                detail=(
                    "User must have DELIVERY_PARTNER role"
                )
            )

        existing = self.repository.get_by_user_id(
            db,
            data.user_id
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Delivery partner profile already exists"
                )
            )

        vehicle = self.repository.get_by_vehicle_number(
            db,
            data.vehicle_number
        )

        if vehicle:
            raise HTTPException(
                status_code=400,
                detail="Vehicle number already exists"
            )

        partner = DeliveryPartner(
            user_id=data.user_id,
            name=data.name,
            phone=data.phone,
            vehicle_type=data.vehicle_type,
            vehicle_number=data.vehicle_number,
            availability_status="AVAILABLE"
        )

        return self.repository.create(
            db,
            partner
        )

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get_partner(
        self,
        db: Session,
        partner_id: int
    ):
        partner = self.repository.get_by_id(
            db,
            partner_id
        )

        if not partner:
            raise HTTPException(
                status_code=404,
                detail="Delivery partner not found"
            )

        return partner

    def get_all(
        self,
        db: Session
    ):
        return self.repository.get_all(db)

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------

    def update_partner(
        self,
        db: Session,
        partner_id: int,
        data,
        current_user: User
    ):
        partner = self.get_partner(
            db,
            partner_id
        )

        # Admin can update anyone
        if current_user.role == "ADMIN":
            pass

        # Delivery partner can update own profile
        elif (
            current_user.role == "DELIVERY_PARTNER"
            and partner.user_id == current_user.id
        ):
            pass

        else:
            raise HTTPException(
                status_code=403,
                detail="You cannot update this profile"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "availability_status" in update_data:

            new_status = (
                update_data["availability_status"]
                .upper()
            )

            if new_status not in self.VALID_STATUSES:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Invalid availability status. "
                        "Use AVAILABLE, BUSY or OFFLINE"
                    )
                )

            update_data[
                "availability_status"
            ] = new_status

        if "vehicle_number" in update_data:

            existing = (
                self.repository
                .get_by_vehicle_number(
                    db,
                    update_data["vehicle_number"]
                )
            )

            if (
                existing
                and existing.id != partner.id
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Vehicle number already exists"
                )

        for field, value in update_data.items():
            setattr(partner, field, value)

        return self.repository.update(
            db,
            partner
        )

    # --------------------------------------------------
    # AVAILABILITY
    # --------------------------------------------------

    def update_availability(
        self,
        db: Session,
        partner_id: int,
        availability_status: str,
        current_user: User
    ):
        partner = self.get_partner(
            db,
            partner_id
        )

        if (
            current_user.role != "ADMIN"
            and partner.user_id != current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You cannot update this partner"
            )

        availability_status = (
            availability_status.upper()
        )

        if availability_status not in self.VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail="Invalid availability status"
            )

        # Cannot manually become AVAILABLE
        # if active order exists
        if availability_status == "AVAILABLE":

            active_order = (
                self.repository.get_active_order(
                    db,
                    partner.id
                )
            )

            if active_order:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Partner has an active delivery"
                    )
                )

        partner.availability_status = (
            availability_status
        )

        return self.repository.update(
            db,
            partner
        )

    # --------------------------------------------------
    # ASSIGN DELIVERY
    # --------------------------------------------------

    def assign_partner(
        self,
        db: Session,
        order_id: int,
        partner_id: int,
        current_user: User
    ):
        if current_user.role not in [
            "ADMIN",
            "RESTAURANT_OWNER",
            "RESTAURANT_STAFF"
        ]:
            raise HTTPException(
                status_code=403,
                detail=(
                    "You are not authorized to assign "
                    "delivery partners"
                )
            )

        order = (
            db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        if order.order_status in [
            "DELIVERED",
            "CANCELLED"
        ]:
            raise HTTPException(
                status_code=400,
                detail="Cannot assign delivery for this order"
            )

        if order.delivery_partner_id:
            raise HTTPException(
                status_code=400,
                detail="Order already has a delivery partner"
            )

        partner = self.get_partner(
            db,
            partner_id
        )

        if not partner.is_active:
            raise HTTPException(
                status_code=400,
                detail="Delivery partner is inactive"
            )

        if (
            partner.availability_status
            != "AVAILABLE"
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Delivery partner is not available"
                )
            )

        # Check conflicting delivery
        active_order = (
            self.repository.get_active_order(
                db,
                partner.id
            )
        )

        if active_order:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Delivery partner already has "
                    "an active delivery"
                )
            )

        order.delivery_partner_id = partner.id

        partner.availability_status = "BUSY"

        db.commit()
        db.refresh(order)

        return order

    # --------------------------------------------------
    # COMPLETE DELIVERY
    # --------------------------------------------------

    def complete_delivery(
        self,
        db: Session,
        order_id: int,
        current_user: User
    ):
        order = (
            db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        if not order.delivery_partner_id:
            raise HTTPException(
                status_code=400,
                detail="No delivery partner assigned"
            )

        partner = self.get_partner(
            db,
            order.delivery_partner_id
        )

        if (
            current_user.role != "ADMIN"
            and partner.user_id != current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail=(
                    "You cannot complete this delivery"
                )
            )

        if order.order_status != "DELIVERED":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Order must be DELIVERED before "
                    "partner becomes available"
                )
            )

        partner.availability_status = "AVAILABLE"

        db.commit()
        db.refresh(partner)

        return {
            "message": "Delivery completed successfully",
            "delivery_partner_id": partner.id,
            "availability_status": partner.availability_status
        }
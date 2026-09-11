from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order import Order
from app.models.tracking import OrderTracking
from app.models.delivery import DeliveryPartner

from app.repositories.tracking_repository import (
    TrackingRepository
)


class TrackingService:

    VALID_STATUSES = [
        "PENDING",
        "ACCEPTED",
        "PREPARING",
        "READY",
        "PICKED_UP",
        "OUT_FOR_DELIVERY",
        "DELIVERED",
        "CANCELLED"
    ]

    TERMINAL_STATUSES = [
        "DELIVERED",
        "CANCELLED"
    ]

    def __init__(self):
        self.repository = TrackingRepository()

    # --------------------------------------------------
    # GET ORDER
    # --------------------------------------------------

    def get_order(
        self,
        db: Session,
        order_id: int
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

        return order

    # --------------------------------------------------
    # CHECK ACCESS
    # --------------------------------------------------

    def check_access(
        self,
        db: Session,
        current_user: User,
        order: Order
    ):
        # Admin
        if current_user.role == "ADMIN":
            return True

        # Customer
        if current_user.role == "CUSTOMER":

            if (
                order.customer
                and order.customer.user_id
                == current_user.id
            ):
                return True

            raise HTTPException(
                status_code=403,
                detail="You cannot access this order"
            )

        # Delivery partner
        if current_user.role == "DELIVERY_PARTNER":

            partner = (
                db.query(DeliveryPartner)
                .filter(
                    DeliveryPartner.user_id
                    == current_user.id
                )
                .first()
            )

            if (
                partner
                and order.delivery_partner_id
                == partner.id
            ):
                return True

            raise HTTPException(
                status_code=403,
                detail="You are not assigned to this order"
            )

        # Restaurant owner/staff
        if current_user.role in [
            "RESTAURANT_OWNER",
            "RESTAURANT_STAFF"
        ]:

            if (
                order.restaurant
                and order.restaurant.owner_id
                == current_user.id
            ):
                return True

            # Staff assignment will be strengthened
            # when restaurant staff mapping is added.

            raise HTTPException(
                status_code=403,
                detail="You cannot access this order"
            )

        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    # --------------------------------------------------
    # CREATE TRACKING
    # --------------------------------------------------

    def create_tracking(
        self,
        db: Session,
        current_user: User,
        order_id: int,
        data
    ):
        order = self.get_order(
            db,
            order_id
        )

        self.check_access(
            db,
            current_user,
            order
        )

        status = data.status.upper()

        if status not in self.VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail="Invalid order status"
            )

        # Terminal orders cannot be tracked again
        if (
            order.order_status
            in self.TERMINAL_STATUSES
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Completed or cancelled orders "
                    "cannot be tracked"
                )
            )

        # Validate status transition
        self.validate_status_transition(
            order.order_status,
            status
        )

        # Delivery partner status restrictions
        if current_user.role == "DELIVERY_PARTNER":

            allowed = [
                "PICKED_UP",
                "OUT_FOR_DELIVERY",
                "DELIVERED"
            ]

            if status not in allowed:
                raise HTTPException(
                    status_code=403,
                    detail=(
                        "Delivery partner cannot set "
                        "this status"
                    )
                )

        tracking = OrderTracking(
            order_id=order.id,
            status=status,
            latitude=data.latitude,
            longitude=data.longitude,
            remarks=data.remarks
        )

        tracking = self.repository.create(
            db,
            tracking
        )

        order.order_status = status

        # If delivered, payment/order completion
        # can be handled by payment workflow.
        db.commit()

        return tracking

    # --------------------------------------------------
    # STATUS TRANSITION
    # --------------------------------------------------

    def validate_status_transition(
        self,
        current_status: str,
        new_status: str
    ):
        allowed_transitions = {
            "PENDING": [
                "ACCEPTED",
                "CANCELLED"
            ],

            "ACCEPTED": [
                "PREPARING",
                "CANCELLED"
            ],

            "PREPARING": [
                "READY",
                "CANCELLED"
            ],

            "READY": [
                "PICKED_UP"
            ],

            "PICKED_UP": [
                "OUT_FOR_DELIVERY"
            ],

            "OUT_FOR_DELIVERY": [
                "DELIVERED"
            ]
        }

        allowed = allowed_transitions.get(
            current_status,
            []
        )

        if new_status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot change order status "
                    f"from {current_status} "
                    f"to {new_status}"
                )
            )

    # --------------------------------------------------
    # GET TRACKING HISTORY
    # --------------------------------------------------

    def get_tracking_history(
        self,
        db: Session,
        current_user: User,
        order_id: int
    ):
        order = self.get_order(
            db,
            order_id
        )

        self.check_access(
            db,
            current_user,
            order
        )

        return self.repository.get_order_tracking(
            db,
            order_id
        )

    # --------------------------------------------------
    # GET LATEST
    # --------------------------------------------------

    def get_latest_tracking(
        self,
        db: Session,
        current_user: User,
        order_id: int
    ):
        order = self.get_order(
            db,
            order_id
        )

        self.check_access(
            db,
            current_user,
            order
        )

        latest = self.repository.get_latest_tracking(
            db,
            order_id
        )

        if not latest:
            raise HTTPException(
                status_code=404,
                detail="No tracking information found"
            )

        return latest

    # --------------------------------------------------
    # UPDATE DRIVER LOCATION
    # --------------------------------------------------

    def update_location(
        self,
        db: Session,
        current_user: User,
        order_id: int,
        latitude: float,
        longitude: float,
        remarks: str | None
    ):
        if current_user.role != "DELIVERY_PARTNER":
            raise HTTPException(
                status_code=403,
                detail=(
                    "Only delivery partners can "
                    "update delivery location"
                )
            )

        order = self.get_order(
            db,
            order_id
        )

        partner = (
            db.query(DeliveryPartner)
            .filter(
                DeliveryPartner.user_id
                == current_user.id
            )
            .first()
        )

        if not partner:
            raise HTTPException(
                status_code=404,
                detail="Delivery partner profile not found"
            )

        if order.delivery_partner_id != partner.id:
            raise HTTPException(
                status_code=403,
                detail=(
                    "You are not assigned to this order"
                )
            )

        if order.order_status in self.TERMINAL_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot update location for "
                    "completed/cancelled order"
                )
            )

        # Update driver's current location
        partner.current_latitude = latitude
        partner.current_longitude = longitude

        latest_status = order.order_status

        tracking = OrderTracking(
            order_id=order.id,
            status=latest_status,
            latitude=latitude,
            longitude=longitude,
            remarks=remarks
        )

        db.add(tracking)
        db.commit()
        db.refresh(tracking)

        return tracking
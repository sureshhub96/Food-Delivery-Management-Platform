from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.tracking import (
    TrackingCreate,
    TrackingResponse,
)
from app.services.tracking_service import TrackingService
from app.services.notification_service import NotificationService
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/tracking",
    tags=["Tracking"]
)

tracking_service = TrackingService()
notification_service = NotificationService()


# ==================================================
# CREATE TRACKING
# ==================================================

@router.post(
    "/orders/{order_id}",
    response_model=TrackingResponse
)
def create_tracking(
    order_id: int,
    request: TrackingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create tracking record
    tracking = tracking_service.create_tracking(
        db,
        current_user,
        order_id,
        request
    )

    # Get order
    order = tracking_service.get_order(
        db,
        order_id
    )

    # Notification messages
    messages = {
        "ACCEPTED": (
            "Order Accepted",
            "Your restaurant has accepted the order."
        ),
        "PREPARING": (
            "Food Preparation Started",
            "Your food is being prepared."
        ),
        "READY": (
            "Order Ready",
            "Your order is ready for pickup."
        ),
        "PICKED_UP": (
            "Order Picked Up",
            "Your delivery partner has picked up your order."
        ),
        "OUT_FOR_DELIVERY": (
            "Out for Delivery",
            "Your order is on the way."
        ),
        "DELIVERED": (
            "Order Delivered",
            "Your order has been delivered successfully."
        ),
        "CANCELLED": (
            "Order Cancelled",
            "Your order has been cancelled."
        )
    }

    # Send notification
    if tracking.status in messages:

        title, message = messages[
            tracking.status
        ]

        background_tasks.add_task(
            notification_service.send_order_notification,
            db,
            order,
            title,
            message,
            f"ORDER_{tracking.status}"
        )

    return tracking


# ==================================================
# GET CURRENT TRACKING
# ==================================================

@router.get(
    "/orders/{order_id}",
    response_model=TrackingResponse
)
def get_tracking(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return tracking_service.get_tracking(
        db,
        current_user,
        order_id
    )


# ==================================================
# GET TRACKING HISTORY
# ==================================================

@router.get(
    "/orders/{order_id}/history",
    response_model=list[TrackingResponse]
)
def get_tracking_history(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return tracking_service.get_tracking_history(
        db,
        current_user,
        order_id
    )


# ==================================================
# UPDATE TRACKING
# ==================================================

@router.put(
    "/orders/{order_id}",
    response_model=TrackingResponse
)
def update_tracking(
    order_id: int,
    request: TrackingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tracking = tracking_service.update_tracking(
        db,
        current_user,
        order_id,
        request
    )

    order = tracking_service.get_order(
        db,
        order_id
    )

    messages = {
        "ACCEPTED": (
            "Order Accepted",
            "Your restaurant has accepted the order."
        ),
        "PREPARING": (
            "Food Preparation Started",
            "Your food is being prepared."
        ),
        "READY": (
            "Order Ready",
            "Your order is ready for pickup."
        ),
        "PICKED_UP": (
            "Order Picked Up",
            "Your delivery partner has picked up your order."
        ),
        "OUT_FOR_DELIVERY": (
            "Out for Delivery",
            "Your order is on the way."
        ),
        "DELIVERED": (
            "Order Delivered",
            "Your order has been delivered successfully."
        ),
        "CANCELLED": (
            "Order Cancelled",
            "Your order has been cancelled."
        )
    }

    if tracking.status in messages:

        title, message = messages[
            tracking.status
        ]

        background_tasks.add_task(
            notification_service.send_order_notification,
            db,
            order,
            title,
            message,
            f"ORDER_{tracking.status}"
        )

    return tracking
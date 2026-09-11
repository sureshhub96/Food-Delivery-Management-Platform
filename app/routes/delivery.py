from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

from app.schemas.delivery import (
    DeliveryPartnerCreate,
    DeliveryPartnerUpdate,
    DeliveryPartnerResponse,
    DeliveryStatusUpdate,
    AssignDeliveryRequest
)

from app.services.delivery_service import (
    DeliveryService
)

from app.utils.dependencies import (
    get_current_user
)


router = APIRouter(
    prefix="/delivery-partners",
    tags=["Delivery Partners"]
)

delivery_service = DeliveryService()


@router.post(
    "",
    response_model=DeliveryPartnerResponse
)
def create_delivery_partner(
    request: DeliveryPartnerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delivery_service.create_partner(
        db,
        request,
        current_user
    )


@router.get(
    "",
    response_model=list[DeliveryPartnerResponse]
)
def get_delivery_partners(
    db: Session = Depends(get_db)
):
    return delivery_service.get_all(db)


@router.get(
    "/{partner_id}",
    response_model=DeliveryPartnerResponse
)
def get_delivery_partner(
    partner_id: int,
    db: Session = Depends(get_db)
):
    return delivery_service.get_partner(
        db,
        partner_id
    )


@router.put(
    "/{partner_id}",
    response_model=DeliveryPartnerResponse
)
def update_delivery_partner(
    partner_id: int,
    request: DeliveryPartnerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delivery_service.update_partner(
        db,
        partner_id,
        request,
        current_user
    )


@router.put(
    "/{partner_id}/availability",
    response_model=DeliveryPartnerResponse
)
def update_availability(
    partner_id: int,
    request: DeliveryStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delivery_service.update_availability(
        db,
        partner_id,
        request.availability_status,
        current_user
    )


@router.post(
    "/orders/{order_id}/assign"
)
def assign_delivery_partner(
    order_id: int,
    request: AssignDeliveryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = delivery_service.assign_partner(
        db,
        order_id,
        request.delivery_partner_id,
        current_user
    )

    return {
        "message": "Delivery partner assigned successfully",
        "order_id": order.id,
        "delivery_partner_id": (
            order.delivery_partner_id
        )
    }


@router.post(
    "/orders/{order_id}/complete"
)
def complete_delivery(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delivery_service.complete_delivery(
        db,
        order_id,
        current_user
    )
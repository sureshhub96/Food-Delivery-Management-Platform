from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

from app.schemas.refund import (
    RefundCreate,
    RefundResponse
)

from app.services.refund_service import (
    RefundService
)

from app.utils.dependencies import (
    get_current_user
)


router = APIRouter(
    prefix="/refunds",
    tags=["Refunds"]
)

refund_service = RefundService()


@router.post(
    "",
    response_model=RefundResponse,
    status_code=201
)
def create_refund(
    request: RefundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return refund_service.create_refund(
        db=db,
        current_user=current_user,
        order_id=request.order_id,
        reason=request.reason
    )


@router.get(
    "/{refund_id}",
    response_model=RefundResponse
)
def get_refund(
    refund_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return refund_service.get_refund(
        db=db,
        current_user=current_user,
        refund_id=refund_id
    )


@router.get(
    "/orders/{order_id}",
    response_model=RefundResponse
)
def get_order_refund(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return refund_service.get_order_refund(
        db=db,
        current_user=current_user,
        order_id=order_id
    )
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse
)

from app.services.payment_service import (
    PaymentService
)

from app.utils.dependencies import (
    get_current_user
)


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

payment_service = PaymentService()


# --------------------------------------------------
# CREATE PAYMENT
# --------------------------------------------------

@router.post(
    "",
    response_model=PaymentResponse,
    status_code=201
)
def create_payment(
    request: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return payment_service.create_payment(
        db,
        current_user,
        request
    )


# --------------------------------------------------
# GET PAYMENT BY ID
# --------------------------------------------------

@router.get(
    "/{payment_id}",
    response_model=PaymentResponse
)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return payment_service.get_payment(
        db,
        current_user,
        payment_id
    )
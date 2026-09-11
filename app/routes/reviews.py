from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

from app.schemas.review import (
    ReviewCreate,
    ReviewResponse
)

from app.services.review_service import (
    ReviewService
)

from app.utils.dependencies import (
    get_current_user
)


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)

review_service = ReviewService()


# --------------------------------------------------
# CREATE REVIEW
# --------------------------------------------------

@router.post(
    "",
    response_model=ReviewResponse,
    status_code=201
)
def create_review(
    request: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return review_service.create_review(
        db,
        current_user,
        request
    )


# --------------------------------------------------
# GET REVIEW
# --------------------------------------------------

@router.get(
    "/{review_id}",
    response_model=ReviewResponse
)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return review_service.get_review(
        db,
        current_user,
        review_id
    )
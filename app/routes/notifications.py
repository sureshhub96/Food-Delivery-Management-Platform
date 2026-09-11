from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.notification_service import NotificationService
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

service = NotificationService()


@router.get("")
def get_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        unread_only=unread_only
    )


@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )


@router.put("/read-all")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.mark_all_as_read(
        db=db,
        user_id=current_user.id
    )
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository


class NotificationService:

    def __init__(self):
        self.repository = NotificationRepository()

    def create_notification(
        self,
        db: Session,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "GENERAL"
    ):
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )

        return self.repository.create(
            db,
            notification
        )

    def get_user_notifications(
        self,
        db: Session,
        user_id: int,
        unread_only: bool = False
    ):
        return self.repository.get_user_notifications(
            db,
            user_id,
            unread_only
        )

    def mark_as_read(
        self,
        db: Session,
        notification_id: int,
        user_id: int
    ):
        notification = self.repository.get_by_id(
            db,
            notification_id
        )

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        if notification.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot update this notification"
            )

        return self.repository.mark_as_read(
            db,
            notification
        )

    def mark_all_as_read(
        self,
        db: Session,
        user_id: int
    ):
        notifications = self.repository.mark_all_as_read(
            db,
            user_id
        )

        return {
            "message": "All notifications marked as read",
            "count": len(notifications)
        }
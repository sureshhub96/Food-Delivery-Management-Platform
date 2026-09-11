from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:

    def create(
        self,
        db: Session,
        notification: Notification
    ):
        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    def get_by_id(
        self,
        db: Session,
        notification_id: int
    ):
        return (
            db.query(Notification)
            .filter(
                Notification.id == notification_id
            )
            .first()
        )

    def get_user_notifications(
        self,
        db: Session,
        user_id: int,
        unread_only: bool = False
    ):
        query = (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id
            )
        )

        if unread_only:
            query = query.filter(
                Notification.is_read == False
            )

        return (
            query
            .order_by(
                Notification.created_at.desc()
            )
            .all()
        )

    def mark_as_read(
        self,
        db: Session,
        notification: Notification
    ):
        notification.is_read = True

        db.commit()
        db.refresh(notification)

        return notification

    def mark_all_as_read(
        self,
        db: Session,
        user_id: int
    ):
        notifications = (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
            .all()
        )

        for notification in notifications:
            notification.is_read = True

        db.commit()

        return notifications
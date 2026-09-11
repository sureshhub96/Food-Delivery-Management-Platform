from sqlalchemy.orm import Session

from app.models.refund import Refund


class RefundRepository:

    def create(
        self,
        db: Session,
        refund: Refund
    ):
        db.add(refund)
        db.commit()
        db.refresh(refund)

        return refund

    def get_by_id(
        self,
        db: Session,
        refund_id: int
    ):
        return (
            db.query(Refund)
            .filter(
                Refund.id == refund_id
            )
            .first()
        )

    def get_by_order_id(
        self,
        db: Session,
        order_id: int
    ):
        return (
            db.query(Refund)
            .filter(
                Refund.order_id == order_id
            )
            .order_by(
                Refund.created_at.desc()
            )
            .first()
        )

    def get_by_transaction_id(
        self,
        db: Session,
        transaction_id: str
    ):
        return (
            db.query(Refund)
            .filter(
                Refund.refund_transaction_id
                == transaction_id
            )
            .first()
        )
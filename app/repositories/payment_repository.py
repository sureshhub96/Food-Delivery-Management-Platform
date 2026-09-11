from sqlalchemy.orm import Session

from app.models.payment import Payment


class PaymentRepository:

    def create(
        self,
        db: Session,
        payment: Payment
    ):
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return payment

    def get_by_id(
        self,
        db: Session,
        payment_id: int
    ):
        return (
            db.query(Payment)
            .filter(
                Payment.id == payment_id
            )
            .first()
        )

    def get_by_order_id(
        self,
        db: Session,
        order_id: int
    ):
        return (
            db.query(Payment)
            .filter(
                Payment.order_id == order_id
            )
            .order_by(
                Payment.created_at.desc()
            )
            .first()
        )

    def get_by_transaction_id(
        self,
        db: Session,
        transaction_id: str
    ):
        return (
            db.query(Payment)
            .filter(
                Payment.transaction_id
                == transaction_id
            )
            .first()
        )

    def update(
        self,
        db: Session,
        payment: Payment
    ):
        db.commit()
        db.refresh(payment)

        return payment
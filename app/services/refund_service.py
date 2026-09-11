from datetime import datetime
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order import Order
from app.models.payment import Payment
from app.models.refund import Refund

from app.repositories.refund_repository import (
    RefundRepository
)


class RefundService:

    def __init__(self):
        self.repository = RefundRepository()

    # --------------------------------------------------
    # GET ORDER
    # --------------------------------------------------

    def get_order(
        self,
        db: Session,
        order_id: int
    ):
        order = (
            db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        return order

    # --------------------------------------------------
    # CHECK ACCESS
    # --------------------------------------------------

    def check_access(
        self,
        current_user: User,
        order: Order
    ):
        if current_user.role == "ADMIN":
            return True

        if current_user.role != "CUSTOMER":
            raise HTTPException(
                status_code=403,
                detail="Only customers can request refunds"
            )

        if not order.customer:
            raise HTTPException(
                status_code=400,
                detail="Customer profile not found"
            )

        if order.customer.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You cannot cancel this order"
            )

        return True

    # --------------------------------------------------
    # CALCULATE REFUND
    # --------------------------------------------------

    def calculate_refund(
        self,
        order: Order
    ):
        status = order.order_status

        if status == "PENDING":
            return float(order.total_amount)

        if status == "ACCEPTED":
            return float(order.total_amount)

        if status == "PREPARING":
            # Limited refund: delivery fee is retained
            refund = (
                float(order.total_amount)
                - float(order.delivery_fee)
            )

            return max(refund, 0)

        if status in [
            "READY",
            "PICKED_UP",
            "OUT_FOR_DELIVERY"
        ]:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Order cannot be cancelled "
                    "at this stage"
                )
            )

        if status == "DELIVERED":
            raise HTTPException(
                status_code=400,
                detail="Delivered orders cannot be cancelled"
            )

        if status == "CANCELLED":
            raise HTTPException(
                status_code=400,
                detail="Order is already cancelled"
            )

        raise HTTPException(
            status_code=400,
            detail="Invalid order status"
        )

    # --------------------------------------------------
    # CANCEL + REFUND
    # --------------------------------------------------

    def cancel_order(
        self,
        db: Session,
        current_user: User,
        order_id: int,
        reason: str | None = None
    ):
        order = self.get_order(
            db,
            order_id
        )

        self.check_access(
            current_user,
            order
        )

        refund_amount = self.calculate_refund(
            order
        )

        # Find successful payment
        payment = (
            db.query(Payment)
            .filter(
                Payment.order_id == order.id,
                Payment.payment_status == "PAID"
            )
            .first()
        )

        # Cancel order
        order.order_status = "CANCELLED"

        # If no payment exists, there is nothing to refund
        if not payment:
            db.commit()
            db.refresh(order)

            return {
                "message": "Order cancelled",
                "order_id": order.id,
                "refund_amount": 0
            }

        # Create refund transaction ID
        refund_transaction_id = (
            "REF-"
            + uuid.uuid4().hex[:12].upper()
        )

        refund = Refund(
            order_id=order.id,
            payment_id=payment.id,
            refund_amount=refund_amount,
            reason=reason,
            refund_status="SUCCESS",
            refund_transaction_id=refund_transaction_id,
            processed_at=datetime.utcnow()
        )

        db.add(refund)

        # Update payment
        payment.payment_status = "REFUNDED"

        db.commit()
        db.refresh(refund)

        return refund

    # --------------------------------------------------
    # CREATE REFUND
    # --------------------------------------------------

    def create_refund(
        self,
        db: Session,
        current_user: User,
        order_id: int,
        reason: str | None = None
    ):
        order = self.get_order(
            db,
            order_id
        )

        self.check_access(
            current_user,
            order
        )

        if order.order_status != "CANCELLED":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Order must be cancelled "
                    "before creating a refund"
                )
            )

        payment = (
            db.query(Payment)
            .filter(
                Payment.order_id == order.id
            )
            .first()
        )

        if not payment:
            raise HTTPException(
                status_code=400,
                detail="No payment found for this order"
            )

        if payment.payment_status == "REFUNDED":
            raise HTTPException(
                status_code=400,
                detail="Payment has already been refunded"
            )

        refund_amount = float(
            payment.amount
        )

        refund_transaction_id = (
            "REF-"
            + uuid.uuid4().hex[:12].upper()
        )

        refund = Refund(
            order_id=order.id,
            payment_id=payment.id,
            refund_amount=refund_amount,
            reason=reason,
            refund_status="SUCCESS",
            refund_transaction_id=refund_transaction_id,
            processed_at=datetime.utcnow()
        )

        db.add(refund)

        payment.payment_status = "REFUNDED"

        db.commit()
        db.refresh(refund)

        return refund

    # --------------------------------------------------
    # GET REFUND
    # --------------------------------------------------

    def get_refund(
        self,
        db: Session,
        current_user: User,
        refund_id: int
    ):
        refund = (
            self.repository.get_by_id(
                db,
                refund_id
            )
        )

        if not refund:
            raise HTTPException(
                status_code=404,
                detail="Refund not found"
            )

        order = self.get_order(
            db,
            refund.order_id
        )

        self.check_access(
            current_user,
            order
        )

        return refund

    # --------------------------------------------------
    # GET ORDER REFUND
    # --------------------------------------------------

    def get_order_refund(
        self,
        db: Session,
        current_user: User,
        order_id: int
    ):
        order = self.get_order(
            db,
            order_id
        )

        self.check_access(
            current_user,
            order
        )

        refund = (
            self.repository.get_by_order_id(
                db,
                order_id
            )
        )

        if not refund:
            raise HTTPException(
                status_code=404,
                detail="No refund found"
            )

        return refund
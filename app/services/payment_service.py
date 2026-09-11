from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order import Order
from app.models.payment import Payment

from app.repositories.payment_repository import PaymentRepository


class PaymentService:

    def __init__(self):
        self.repository = PaymentRepository()

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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        return order

    # --------------------------------------------------
    # CHECK CUSTOMER ACCESS
    # --------------------------------------------------

    def check_order_access(
        self,
        current_user: User,
        order: Order
    ):
        if current_user.role == "ADMIN":
            return True

        if current_user.role != "CUSTOMER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only customers can make payments"
            )

        if not order.customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer profile not found"
            )

        if order.customer.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot pay for this order"
            )

        return True

    # --------------------------------------------------
    # CREATE PAYMENT
    # --------------------------------------------------

    def create_payment(
        self,
        db: Session,
        current_user: User,
        data
    ):
        order = self.get_order(
            db,
            data.order_id
        )

        self.check_order_access(
            current_user,
            order
        )

        # Cancelled orders cannot be paid
        if order.order_status == "CANCELLED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cancelled orders cannot be paid"
            )

        # Delivered orders cannot be paid again
        if order.order_status == "DELIVERED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delivered order cannot be paid again"
            )

        # Check if order is already paid
        if order.payment_status == "PAID":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order has already been paid"
            )

        # --------------------------------------------------
        # AMOUNT VALIDATION
        # --------------------------------------------------

        order_total = round(
            float(order.total_amount),
            2
        )

        payment_amount = round(
            float(data.amount),
            2
        )

        if payment_amount != order_total:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Payment amount must match "
                    f"order total of {order_total}"
                )
            )

        # --------------------------------------------------
        # DUPLICATE TRANSACTION CHECK
        # --------------------------------------------------

        if data.transaction_id:

            existing_transaction = (
                self.repository.get_by_transaction_id(
                    db,
                    data.transaction_id
                )
            )

            if existing_transaction:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Transaction ID already exists"
                )

        # --------------------------------------------------
        # EXISTING PAYMENT CHECK
        # --------------------------------------------------

        existing_payment = (
            self.repository.get_by_order_id(
                db,
                order.id
            )
        )

        if existing_payment:

            if existing_payment.payment_status == "SUCCESS":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order payment already completed"
                )

            if existing_payment.payment_status == "PENDING":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "A payment is already pending "
                        "for this order"
                    )
                )

        # --------------------------------------------------
        # CREATE PAYMENT
        # --------------------------------------------------

        payment = Payment(
            order_id=order.id,
            amount=payment_amount,
            payment_method=data.payment_method,
            transaction_id=data.transaction_id,
            payment_status="SUCCESS",
            paid_at=datetime.utcnow()
        )

        payment = self.repository.create(
            db,
            payment
        )

        # --------------------------------------------------
        # UPDATE ORDER
        # --------------------------------------------------

        order.payment_status = "PAID"

        db.commit()
        db.refresh(order)

        return payment

    # --------------------------------------------------
    # GET PAYMENT
    # --------------------------------------------------

    def get_payment(
        self,
        db: Session,
        current_user: User,
        payment_id: int
    ):
        payment = self.repository.get_by_id(
            db,
            payment_id
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        order = self.get_order(
            db,
            payment.order_id
        )

        self.check_order_access(
            current_user,
            order
        )

        return payment

    # --------------------------------------------------
    # GET ORDER PAYMENT
    # --------------------------------------------------

    def get_order_payment(
        self,
        db: Session,
        current_user: User,
        order_id: int
    ):
        order = self.get_order(
            db,
            order_id
        )

        self.check_order_access(
            current_user,
            order
        )

        payment = self.repository.get_by_order_id(
            db,
            order_id
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No payment found for this order"
            )

        return payment
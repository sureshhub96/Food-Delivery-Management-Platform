from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.order import Order
from app.models.customer import Customer
from app.repositories.review_repository import ReviewRepository


class ReviewService:

    def __init__(self):
        self.repository = ReviewRepository()

    # --------------------------------------------------
    # CREATE REVIEW
    # --------------------------------------------------

    def create_review(
        self,
        db: Session,
        current_user,
        request
    ):
        # Only customers can create reviews
        if current_user.role != "CUSTOMER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only customers can create reviews"
            )

        # Get customer profile
        customer = (
            db.query(Customer)
            .filter(
                Customer.user_id == current_user.id
            )
            .first()
        )

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found"
            )

        # Get order
        order = (
            db.query(Order)
            .filter(
                Order.id == request.order_id
            )
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        # Verify order belongs to customer
        if order.customer_id != customer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can review only your own orders"
            )

        # Review allowed only after delivery
        if order.order_status != "DELIVERED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can review only delivered orders"
            )

        # Validate target
        target_fields = [
            request.restaurant_id,
            request.food_item_id,
            request.delivery_partner_id
        ]

        if sum(
            value is not None
            for value in target_fields
        ) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Provide exactly one review target: "
                    "restaurant_id, food_item_id, or "
                    "delivery_partner_id"
                )
            )

        # Restaurant review
        if request.restaurant_id is not None:

            if request.restaurant_id != order.restaurant_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Restaurant does not belong to this order"
                )

        # Delivery partner review
        if request.delivery_partner_id is not None:

            if (
                order.delivery_partner_id
                != request.delivery_partner_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Delivery partner was not assigned "
                        "to this order"
                    )
                )

        # Check duplicate review
        existing_review = self.repository.get_existing_review(
            db=db,
            customer_id=customer.id,
            order_id=request.order_id
        )

        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this order"
            )

        # Create review
        review = Review(
            customer_id=customer.id,
            order_id=request.order_id,
            restaurant_id=request.restaurant_id,
            food_item_id=request.food_item_id,
            delivery_partner_id=request.delivery_partner_id,
            rating=request.rating,
            review=request.review
        )

        return self.repository.create(
            db,
            review
        )

    # --------------------------------------------------
    # GET REVIEW
    # --------------------------------------------------

    def get_review(
        self,
        db: Session,
        current_user,
        review_id: int
    ):
        review = self.repository.get_by_id(
            db,
            review_id
        )

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # Admin can view any review
        if current_user.role == "ADMIN":
            return review

        # Customer can view only own review
        if current_user.role == "CUSTOMER":

            customer = (
                db.query(Customer)
                .filter(
                    Customer.user_id == current_user.id
                )
                .first()
            )

            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer profile not found"
                )

            if review.customer_id != customer.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You cannot view this review"
                )

            return review

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this review"
        )
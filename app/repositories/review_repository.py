from sqlalchemy.orm import Session

from app.models.review import Review


class ReviewRepository:

    def create(
        self,
        db: Session,
        review: Review
    ):
        db.add(review)
        db.commit()
        db.refresh(review)

        return review

    def get_by_id(
        self,
        db: Session,
        review_id: int
    ):
        return (
            db.query(Review)
            .filter(
                Review.id == review_id
            )
            .first()
        )

    def get_by_order_customer(
        self,
        db: Session,
        order_id: int,
        customer_id: int
    ):
        return (
            db.query(Review)
            .filter(
                Review.order_id == order_id,
                Review.customer_id == customer_id
            )
            .all()
        )

    def get_duplicate(
        self,
        db: Session,
        order_id: int,
        customer_id: int,
        restaurant_id=None,
        food_item_id=None,
        delivery_partner_id=None
    ):
        query = (
            db.query(Review)
            .filter(
                Review.order_id == order_id,
                Review.customer_id == customer_id
            )
        )

        if restaurant_id is not None:
            query = query.filter(
                Review.restaurant_id == restaurant_id
            )

        if food_item_id is not None:
            query = query.filter(
                Review.food_item_id == food_item_id
            )

        if delivery_partner_id is not None:
            query = query.filter(
                Review.delivery_partner_id
                == delivery_partner_id
            )

        return query.first()

    def get_restaurant_reviews(
        self,
        db: Session,
        restaurant_id: int
    ):
        return (
            db.query(Review)
            .filter(
                Review.restaurant_id
                == restaurant_id
            )
            .order_by(
                Review.created_at.desc()
            )
            .all()
        )

    def get_food_item_reviews(
        self,
        db: Session,
        food_item_id: int
    ):
        return (
            db.query(Review)
            .filter(
                Review.food_item_id
                == food_item_id
            )
            .order_by(
                Review.created_at.desc()
            )
            .all()
        )

    def get_delivery_partner_reviews(
        self,
        db: Session,
        delivery_partner_id: int
    ):
        return (
            db.query(Review)
            .filter(
                Review.delivery_partner_id
                == delivery_partner_id
            )
            .order_by(
                Review.created_at.desc()
            )
            .all()
        )
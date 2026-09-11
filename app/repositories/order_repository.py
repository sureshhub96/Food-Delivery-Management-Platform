from datetime import datetime

from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem


class OrderRepository:

    def create_order(
        self,
        db: Session,
        order: Order
    ):
        db.add(order)
        db.commit()
        db.refresh(order)

        return order

    def create_order_item(
        self,
        db: Session,
        item: OrderItem
    ):
        db.add(item)
        db.commit()
        db.refresh(item)

        return item

    def get_by_id(
        self,
        db: Session,
        order_id: int
    ):
        return (
            db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )

    def get_customer_orders(
        self,
        db: Session,
        customer_id: int
    ):
        return (
            db.query(Order)
            .filter(
                Order.customer_id == customer_id
            )
            .order_by(
                Order.created_at.desc()
            )
            .all()
        )

    def update(
        self,
        db: Session,
        order: Order
    ):
        db.commit()
        db.refresh(order)

        return order

    def search_orders(
        self,
        db: Session,
        customer_id: int | None = None,
        restaurant_id: int | None = None,
        order_status: str | None = None,
        payment_status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        limit: int = 10,
        sort_order: str = "desc"
    ):
        # Start query
        query = db.query(Order)

        # -------------------------
        # Filter by customer
        # -------------------------
        if customer_id is not None:
            query = query.filter(
                Order.customer_id == customer_id
            )

        # -------------------------
        # Filter by restaurant
        # -------------------------
        if restaurant_id is not None:
            query = query.filter(
                Order.restaurant_id == restaurant_id
            )

        # -------------------------
        # Filter by order status
        # -------------------------
        if order_status:
            query = query.filter(
                Order.order_status
                == order_status.upper()
            )

        # -------------------------
        # Filter by payment status
        # -------------------------
        if payment_status:
            query = query.filter(
                Order.payment_status
                == payment_status.upper()
            )

        # -------------------------
        # Filter by start date
        # -------------------------
        if start_date:
            query = query.filter(
                Order.created_at >= start_date
            )

        # -------------------------
        # Filter by end date
        # -------------------------
        if end_date:
            query = query.filter(
                Order.created_at <= end_date
            )

        # -------------------------
        # Total records
        # -------------------------
        total = query.count()

        # -------------------------
        # Sorting
        # -------------------------
        if sort_order.lower() == "asc":
            query = query.order_by(
                Order.created_at.asc()
            )
        else:
            query = query.order_by(
                Order.created_at.desc()
            )

        # -------------------------
        # Pagination validation
        # -------------------------
        if page < 1:
            page = 1

        if limit < 1:
            limit = 10

        if limit > 100:
            limit = 100

        # -------------------------
        # Pagination
        # -------------------------
        offset = (page - 1) * limit

        items = (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )

        return items, total
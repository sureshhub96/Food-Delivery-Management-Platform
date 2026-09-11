from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.delivery import DeliveryPartner
from app.models.order import Order, OrderItem
from app.models.payment import Payment
from app.models.refund import Refund
from app.models.menu import FoodItem


class AnalyticsService:

    # --------------------------------------------------
    # RESTAURANT DASHBOARD
    # --------------------------------------------------

    def get_restaurant_dashboard(
        self,
        db: Session,
        restaurant_id: int
    ):
        restaurant = (
            db.query(Restaurant)
            .filter(
                Restaurant.id == restaurant_id,
                Restaurant.is_deleted == False
            )
            .first()
        )

        if not restaurant:
            raise ValueError("Restaurant not found")

        orders = (
            db.query(Order)
            .filter(
                Order.restaurant_id == restaurant_id
            )
            .all()
        )

        total_orders = len(orders)

        delivered_orders = sum(
            1 for order in orders
            if order.order_status == "DELIVERED"
        )

        cancelled_orders = sum(
            1 for order in orders
            if order.order_status == "CANCELLED"
        )

        pending_orders = sum(
            1 for order in orders
            if order.order_status == "PENDING"
        )

        total_revenue = sum(
            float(order.total_amount or 0)
            for order in orders
            if order.payment_status == "PAID"
        )

        average_order_value = (
            total_revenue / delivered_orders
            if delivered_orders > 0
            else 0.0
        )

        # --------------------------------------------------
        # TOP FOOD ITEMS
        # --------------------------------------------------

        top_foods_query = (
            db.query(
                FoodItem.id.label("food_item_id"),
                FoodItem.name.label("food_name"),
                func.sum(OrderItem.quantity).label(
                    "quantity_sold"
                ),
                func.sum(
                    OrderItem.quantity * OrderItem.unit_price
                ).label("revenue")
            )
            .join(
                OrderItem,
                OrderItem.food_item_id == FoodItem.id
            )
            .join(
                Order,
                Order.id == OrderItem.order_id
            )
            .filter(
                Order.restaurant_id == restaurant_id,
                Order.order_status == "DELIVERED"
            )
            .group_by(
                FoodItem.id,
                FoodItem.name
            )
            .order_by(
                func.sum(
                    OrderItem.quantity
                ).desc()
            )
            .limit(10)
            .all()
        )

        top_foods = [
            {
                "food_item_id": row.food_item_id,
                "food_name": row.food_name,
                "quantity_sold": int(
                    row.quantity_sold or 0
                ),
                "revenue": float(
                    row.revenue or 0
                )
            }
            for row in top_foods_query
        ]

        # --------------------------------------------------
        # ORDER STATUS SUMMARY
        # --------------------------------------------------

        order_status_summary = {}

        for order in orders:
            status = order.order_status

            order_status_summary[status] = (
                order_status_summary.get(status, 0) + 1
            )

        return {
            "restaurant_id": restaurant_id,
            "total_orders": total_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "pending_orders": pending_orders,
            "total_revenue": round(total_revenue, 2),
            "average_order_value": round(
                average_order_value,
                2
            ),
            "top_foods": top_foods,
            "order_status_summary": order_status_summary
        }

    # --------------------------------------------------
    # ADMIN DASHBOARD
    # --------------------------------------------------

    def get_admin_dashboard(
        self,
        db: Session
    ):
        total_users = (
            db.query(User)
            .count()
        )

        total_customers = (
            db.query(User)
            .filter(
                User.role == "CUSTOMER"
            )
            .count()
        )

        total_restaurants = (
            db.query(Restaurant)
            .filter(
                Restaurant.is_deleted == False
            )
            .count()
        )

        total_delivery_partners = (
            db.query(DeliveryPartner)
            .count()
        )

        total_orders = (
            db.query(Order)
            .count()
        )

        delivered_orders = (
            db.query(Order)
            .filter(
                Order.order_status == "DELIVERED"
            )
            .count()
        )

        cancelled_orders = (
            db.query(Order)
            .filter(
                Order.order_status == "CANCELLED"
            )
            .count()
        )

        pending_orders = (
            db.query(Order)
            .filter(
                Order.order_status == "PENDING"
            )
            .count()
        )

        # --------------------------------------------------
        # SUCCESSFUL PAYMENTS
        # --------------------------------------------------

        successful_payments = (
            db.query(
                func.coalesce(
                    func.sum(Payment.amount),
                    0
                )
            )
            .filter(
                Payment.payment_status == "SUCCESS"
            )
            .scalar()
        )

        # --------------------------------------------------
        # REFUNDS
        # --------------------------------------------------

        total_refunds = (
            db.query(
                func.coalesce(
                    func.sum(Refund.refund_amount),
                    0
                )
            )
            .filter(
                Refund.refund_status == "SUCCESS"
            )
            .scalar()
        )

        return {
            "total_users": total_users,
            "total_customers": total_customers,
            "total_restaurants": total_restaurants,
            "total_delivery_partners":
                total_delivery_partners,
            "total_orders": total_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "pending_orders": pending_orders,
            "total_revenue": round(
                float(successful_payments or 0),
                2
            ),
            "successful_payments": round(
                float(successful_payments or 0),
                2
            ),
            "total_refunds": round(
                float(total_refunds or 0),
                2
            )
        }

    # --------------------------------------------------
    # MONTHLY ORDERS
    # --------------------------------------------------

    def get_monthly_orders(
        self,
        db: Session,
        year: int
    ):
        results = (
            db.query(
                extract(
                    "month",
                    Order.created_at
                ).label("month"),
                func.count(
                    Order.id
                ).label("order_count")
            )
            .filter(
                extract(
                    "year",
                    Order.created_at
                ) == year
            )
            .group_by(
                extract(
                    "month",
                    Order.created_at
                )
            )
            .order_by(
                extract(
                    "month",
                    Order.created_at
                )
            )
            .all()
        )

        return [
            {
                "month": str(
                    int(row.month)
                ),
                "order_count": int(
                    row.order_count
                )
            }
            for row in results
        ]

    # --------------------------------------------------
    # MONTHLY REVENUE
    # --------------------------------------------------

    def get_monthly_revenue(
        self,
        db: Session,
        year: int
    ):
        results = (
            db.query(
                extract(
                    "month",
                    Payment.paid_at
                ).label("month"),
                func.sum(
                    Payment.amount
                ).label("revenue")
            )
            .filter(
                extract(
                    "year",
                    Payment.paid_at
                ) == year,
                Payment.payment_status == "SUCCESS"
            )
            .group_by(
                extract(
                    "month",
                    Payment.paid_at
                )
            )
            .order_by(
                extract(
                    "month",
                    Payment.paid_at
                )
            )
            .all()
        )

        return [
            {
                "month": str(
                    int(row.month)
                ),
                "revenue": float(
                    row.revenue or 0
                )
            }
            for row in results
        ]


# --------------------------------------------------
# SERVICE INSTANCE
# --------------------------------------------------

analytics_service = AnalyticsService()
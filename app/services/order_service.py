from datetime import datetime
from math import ceil

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.address import Address
from app.models.restaurant import Restaurant

from app.repositories.customer_repository import CustomerRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.coupon_repository import CouponRepository


class OrderService:

    TAX_PERCENTAGE = 5.0
    BASE_DELIVERY_FEE = 40.0

    def __init__(self):
        self.customer_repo = CustomerRepository()
        self.cart_repo = CartRepository()
        self.order_repo = OrderRepository()
        self.coupon_repo = CouponRepository()

    # ==================================================
    # CUSTOMER
    # ==================================================

    def get_customer(
        self,
        db: Session,
        current_user: User
    ):
        customer = self.customer_repo.get_by_user_id(
            db,
            current_user.id
        )

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer profile not found"
            )

        return customer

    # ==================================================
    # CREATE ORDER
    # ==================================================

    def create_order(
        self,
        db: Session,
        current_user: User,
        address_id: int,
        coupon_code: str | None = None
    ):

        if current_user.role != "CUSTOMER":
            raise HTTPException(
                status_code=403,
                detail="Only customers can place orders"
            )

        customer = self.get_customer(
            db,
            current_user
        )

        # --------------------------------------------------
        # GET CART
        # --------------------------------------------------

        cart = self.cart_repo.get_by_customer_id(
            db,
            customer.id
        )

        if not cart or not cart.items:
            raise HTTPException(
                status_code=400,
                detail="Cart is empty"
            )

        # --------------------------------------------------
        # ADDRESS VALIDATION
        # --------------------------------------------------

        address = (
            db.query(Address)
            .filter(
                Address.id == address_id,
                Address.customer_id == customer.id
            )
            .first()
        )

        if not address:
            raise HTTPException(
                status_code=400,
                detail="Invalid delivery address"
            )

        # --------------------------------------------------
        # RESTAURANT VALIDATION
        # --------------------------------------------------

        restaurant = (
            db.query(Restaurant)
            .filter(
                Restaurant.id == cart.restaurant_id,
                Restaurant.is_deleted == False
            )
            .first()
        )

        if not restaurant:
            raise HTTPException(
                status_code=400,
                detail="Restaurant not found"
            )

        if restaurant.status in {
            "CLOSED",
            "TEMPORARILY_UNAVAILABLE"
        }:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Restaurant is currently "
                    "not accepting orders"
                )
            )

        # --------------------------------------------------
        # FOOD ITEM VALIDATION
        # --------------------------------------------------

        subtotal = 0.0

        for cart_item in cart.items:

            food_item = cart_item.food_item

            if not food_item:
                raise HTTPException(
                    status_code=400,
                    detail="Food item no longer exists"
                )

            if food_item.is_deleted:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"{food_item.name} "
                        "is no longer available"
                    )
                )

            if not food_item.availability:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"{food_item.name} "
                        "is currently unavailable"
                    )
                )

            if food_item.restaurant_id != restaurant.id:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid restaurant item in cart"
                )

            item_total = (
                float(food_item.price)
                * cart_item.quantity
            )

            subtotal += item_total

        subtotal = round(subtotal, 2)

        # ==================================================
        # COUPON
        # ==================================================

        discount = 0.0
        applied_coupon = None

        if coupon_code:

            applied_coupon = self.coupon_repo.get_by_code(
                db,
                coupon_code.upper()
            )

            if not applied_coupon:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid coupon code"
                )

            now = datetime.utcnow()

            if not applied_coupon.is_active:
                raise HTTPException(
                    status_code=400,
                    detail="Coupon is inactive"
                )

            if now < applied_coupon.start_date:
                raise HTTPException(
                    status_code=400,
                    detail="Coupon is not active yet"
                )

            if now > applied_coupon.end_date:
                raise HTTPException(
                    status_code=400,
                    detail="Coupon has expired"
                )

            if (
                applied_coupon.usage_limit is not None
                and applied_coupon.used_count
                >= applied_coupon.usage_limit
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Coupon usage limit exceeded"
                )

            if (
                subtotal
                < applied_coupon.min_order_amount
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Minimum order amount is "
                        f"{applied_coupon.min_order_amount}"
                    )
                )

            # Percentage discount
            if applied_coupon.discount_type == "PERCENTAGE":

                discount = (
                    subtotal
                    * applied_coupon.discount_value
                    / 100
                )

            # Fixed discount
            else:
                discount = (
                    applied_coupon.discount_value
                )

            # Maximum discount
            if applied_coupon.max_discount is not None:
                discount = min(
                    discount,
                    applied_coupon.max_discount
                )

            # Discount cannot exceed subtotal
            discount = min(
                discount,
                subtotal
            )

            discount = round(
                discount,
                2
            )

        # ==================================================
        # DELIVERY FEE
        # ==================================================

        delivery_fee = self.BASE_DELIVERY_FEE

        # Free delivery for orders >= 1000
        if subtotal >= 1000:
            delivery_fee = 0.0

        # ==================================================
        # TAX
        # ==================================================

        taxable_amount = max(
            subtotal - discount,
            0
        )

        tax = (
            taxable_amount
            * self.TAX_PERCENTAGE
            / 100
        )

        tax = round(
            tax,
            2
        )

        # ==================================================
        # FINAL TOTAL
        # ==================================================

        total_amount = (
            subtotal
            + tax
            + delivery_fee
            - discount
        )

        total_amount = round(
            max(total_amount, 0),
            2
        )

        # ==================================================
        # CREATE ORDER
        # ==================================================

        order = Order(
            customer_id=customer.id,
            restaurant_id=restaurant.id,
            address_id=address.id,

            subtotal=subtotal,
            delivery_fee=delivery_fee,
            discount=discount,
            tax=tax,
            total_amount=total_amount,

            order_status="PENDING",
            payment_status="PENDING",

            coupon_code=(
                applied_coupon.coupon_code
                if applied_coupon
                else None
            )
        )

        self.order_repo.create_order(
            db,
            order
        )

        # ==================================================
        # CREATE ORDER ITEMS
        # ==================================================

        for cart_item in cart.items:

            food_item = cart_item.food_item

            item_total = round(
                float(food_item.price)
                * cart_item.quantity,
                2
            )

            order_item = OrderItem(
                order_id=order.id,
                food_item_id=food_item.id,
                food_name=food_item.name,
                price=float(food_item.price),
                quantity=cart_item.quantity,
                item_total=item_total
            )

            self.order_repo.create_order_item(
                db,
                order_item
            )

        # ==================================================
        # COUPON USAGE
        # ==================================================

        if applied_coupon:

            applied_coupon.used_count += 1

            db.commit()

        # ==================================================
        # CLEAR CART
        # ==================================================

        cart.items.clear()
        cart.restaurant_id = None

        db.commit()

        db.refresh(order)

        return order

    # ==================================================
    # GET ORDER
    # ==================================================

    def get_order(
        self,
        db: Session,
        current_user: User,
        order_id: int
    ):

        order = self.order_repo.get_by_id(
            db,
            order_id
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        # Admin can access any order
        if current_user.role == "ADMIN":
            return order

        # Customer can access only own order
        if current_user.role == "CUSTOMER":

            customer = self.get_customer(
                db,
                current_user
            )

            if order.customer_id != customer.id:
                raise HTTPException(
                    status_code=403,
                    detail="You cannot access this order"
                )

            return order

        raise HTTPException(
            status_code=403,
            detail="You cannot access this order"
        )

    # ==================================================
    # GET MY ORDERS
    # ==================================================

    def get_my_orders(
        self,
        db: Session,
        current_user: User
    ):

        if current_user.role != "CUSTOMER":
            raise HTTPException(
                status_code=403,
                detail="Only customers can view their orders"
            )

        customer = self.get_customer(
            db,
            current_user
        )

        return self.order_repo.get_customer_orders(
            db,
            customer.id
        )

    # ==================================================
    # CANCEL ORDER
    # ==================================================

    def cancel_order(
        self,
        db: Session,
        current_user: User,
        order_id: int
    ):

        order = self.get_order(
            db,
            current_user,
            order_id
        )

        # Already completed/cancelled
        if order.order_status in {
            "DELIVERED",
            "CANCELLED"
        }:
            raise HTTPException(
                status_code=400,
                detail="Order cannot be cancelled"
            )

        # Too late to cancel
        if order.order_status in {
            "READY",
            "PICKED_UP",
            "OUT_FOR_DELIVERY"
        }:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Order cannot be cancelled "
                    "at this stage"
                )
            )

        order.order_status = "CANCELLED"

        # --------------------------------------------------
        # RESTORE COUPON USAGE
        # --------------------------------------------------

        if order.coupon_code:

            coupon = self.coupon_repo.get_by_code(
                db,
                order.coupon_code
            )

            if coupon and coupon.used_count > 0:
                coupon.used_count -= 1

        self.order_repo.update(
            db,
            order
        )

        return order

    # ==================================================
    # SEARCH ORDERS
    # ==================================================

    def search_orders(
        self,
        db: Session,
        current_user: User,
        restaurant_id: int | None = None,
        order_status: str | None = None,
        payment_status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        limit: int = 10,
        sort_order: str = "desc"
    ):

        # --------------------------------------------------
        # PAGINATION VALIDATION
        # --------------------------------------------------

        if page < 1:
            page = 1

        if limit < 1:
            limit = 10

        if limit > 100:
            limit = 100

        # --------------------------------------------------
        # ROLE VALIDATION
        # --------------------------------------------------

        customer_id = None

        if current_user.role == "CUSTOMER":

            customer = self.get_customer(
                db,
                current_user
            )

            customer_id = customer.id

        elif current_user.role not in {
            "ADMIN",
            "RESTAURANT_OWNER",
            "RESTAURANT_STAFF"
        }:
            raise HTTPException(
                status_code=403,
                detail="Not authorized"
            )

        # --------------------------------------------------
        # SEARCH ORDERS
        # --------------------------------------------------

        items, total = (
            self.order_repo.search_orders(
                db=db,
                customer_id=customer_id,
                restaurant_id=restaurant_id,
                order_status=order_status,
                payment_status=payment_status,
                start_date=start_date,
                end_date=end_date,
                page=page,
                limit=limit,
                sort_order=sort_order
            )
        )

        # --------------------------------------------------
        # TOTAL PAGES
        # --------------------------------------------------

        total_pages = (
            ceil(total / limit)
            if total > 0
            else 0
        )

        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        }
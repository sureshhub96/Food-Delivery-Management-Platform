from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.menu import FoodItem
from app.repositories.cart_repository import CartRepository
from app.repositories.customer_repository import CustomerRepository


class CartService:

    def __init__(self):
        self.cart_repo = CartRepository()
        self.customer_repo = CustomerRepository()

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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found. Please create a customer profile first."
            )

        return customer

    def get_or_create_cart(
        self,
        db: Session,
        customer_id: int
    ):
        cart = self.cart_repo.get_by_customer_id(
            db,
            customer_id
        )

        if not cart:
            cart = self.cart_repo.create_cart(
                db,
                customer_id
            )

        return cart

    def add_item(
        self,
        db: Session,
        current_user: User,
        food_item_id: int,
        quantity: int
    ):
        if current_user.role != "CUSTOMER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only customers can manage carts"
            )

        if quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than 0"
            )

        customer = self.get_customer(
            db,
            current_user
        )

        food_item = (
            db.query(FoodItem)
            .filter(
                FoodItem.id == food_item_id,
                FoodItem.is_deleted == False
            )
            .first()
        )

        if not food_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food item not found"
            )

        if not food_item.availability:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Food item is currently unavailable"
            )

        restaurant = food_item.restaurant

        if not restaurant or restaurant.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Restaurant is not available"
            )

        if restaurant.status in {
            "CLOSED",
            "TEMPORARILY_UNAVAILABLE"
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Restaurant is currently not accepting orders"
            )

        cart = self.get_or_create_cart(
            db,
            customer.id
        )

        # One restaurant per cart
        if (
            cart.restaurant_id is not None
            and cart.restaurant_id != food_item.restaurant_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart can contain items from only one restaurant"
            )

        # First item determines restaurant
        if cart.restaurant_id is None:
            cart.restaurant_id = food_item.restaurant_id

            db.commit()
            db.refresh(cart)

        existing_item = self.cart_repo.get_item(
            db,
            cart.id,
            food_item_id
        )

        if existing_item:
            existing_item.quantity += quantity

            db.commit()
            db.refresh(existing_item)

            return existing_item

        return self.cart_repo.create_item(
            db,
            cart.id,
            food_item_id,
            quantity
        )

    def get_cart(
        self,
        db: Session,
        current_user: User
    ):
        if current_user.role != "CUSTOMER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only customers can view carts"
            )

        customer = self.get_customer(
            db,
            current_user
        )

        return self.get_or_create_cart(
            db,
            customer.id
        )

    def update_item(
        self,
        db: Session,
        current_user: User,
        item_id: int,
        quantity: int
    ):
        if current_user.role != "CUSTOMER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only customers can manage carts"
            )

        if quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than 0"
            )

        customer = self.get_customer(
            db,
            current_user
        )

        cart = self.get_or_create_cart(
            db,
            customer.id
        )

        item = self.cart_repo.get_item_by_id(
            db,
            cart.id,
            item_id
        )

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )

        if item.food_item.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Food item has been removed"
            )

        if not item.food_item.availability:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Food item is currently unavailable"
            )

        return self.cart_repo.update_item(
            db,
            item,
            quantity
        )

    def remove_item(
        self,
        db: Session,
        current_user: User,
        item_id: int
    ):
        if current_user.role != "CUSTOMER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only customers can manage carts"
            )

        customer = self.get_customer(
            db,
            current_user
        )

        cart = self.get_or_create_cart(
            db,
            customer.id
        )

        item = self.cart_repo.get_item_by_id(
            db,
            cart.id,
            item_id
        )

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )

        self.cart_repo.delete_item(
            db,
            item
        )

        db.refresh(cart)

        # If cart becomes empty, reset restaurant
        if len(cart.items) == 0:
            cart.restaurant_id = None
            db.commit()
            db.refresh(cart)

        return {
            "message": "Cart item removed successfully"
        }

    def clear_cart(
        self,
        db: Session,
        current_user: User
    ):
        if current_user.role != "CUSTOMER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only customers can manage carts"
            )

        customer = self.get_customer(
            db,
            current_user
        )

        cart = self.get_or_create_cart(
            db,
            customer.id
        )

        self.cart_repo.clear_cart(
            db,
            cart
        )

        return {
            "message": "Cart cleared successfully"
        }

    def calculate_subtotal(
        self,
        cart
    ):
        subtotal = 0.0

        for item in cart.items:
            subtotal += (
                float(item.food_item.price)
                * item.quantity
            )

        return round(subtotal, 2)
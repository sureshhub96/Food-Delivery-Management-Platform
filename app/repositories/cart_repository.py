from sqlalchemy.orm import Session

from app.models.cart import Cart, CartItem


class CartRepository:

    def get_by_customer_id(
        self,
        db: Session,
        customer_id: int
    ):
        return (
            db.query(Cart)
            .filter(Cart.customer_id == customer_id)
            .first()
        )

    def create_cart(
        self,
        db: Session,
        customer_id: int
    ):
        cart = Cart(customer_id=customer_id)

        db.add(cart)
        db.commit()
        db.refresh(cart)

        return cart

    def get_item(
        self,
        db: Session,
        cart_id: int,
        food_item_id: int
    ):
        return (
            db.query(CartItem)
            .filter(
                CartItem.cart_id == cart_id,
                CartItem.food_item_id == food_item_id
            )
            .first()
        )

    def get_item_by_id(
        self,
        db: Session,
        cart_id: int,
        item_id: int
    ):
        return (
            db.query(CartItem)
            .filter(
                CartItem.id == item_id,
                CartItem.cart_id == cart_id
            )
            .first()
        )

    def create_item(
        self,
        db: Session,
        cart_id: int,
        food_item_id: int,
        quantity: int
    ):
        item = CartItem(
            cart_id=cart_id,
            food_item_id=food_item_id,
            quantity=quantity
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        return item

    def update_item(
        self,
        db: Session,
        item: CartItem,
        quantity: int
    ):
        item.quantity = quantity

        db.commit()
        db.refresh(item)

        return item

    def delete_item(
        self,
        db: Session,
        item: CartItem
    ):
        db.delete(item)
        db.commit()

    def clear_cart(
        self,
        db: Session,
        cart: Cart
    ):
        cart.items.clear()
        cart.restaurant_id = None

        db.commit()
        db.refresh(cart)

        return cart
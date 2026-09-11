from math import ceil

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.menu import FoodItem
from app.models.restaurant import Restaurant
from app.repositories.menu_repository import MenuRepository
from app.schemas.menu import FoodItemCreate, FoodItemUpdate


class MenuService:

    def __init__(self):
        self.repository = MenuRepository()

    # ==================================================
    # Validate Restaurant
    # ==================================================

    def validate_restaurant(
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
            raise HTTPException(
                status_code=404,
                detail="Restaurant not found"
            )

        return restaurant

    # ==================================================
    # Create Food Item
    # ==================================================

    def create_food_item(
        self,
        db: Session,
        data: FoodItemCreate,
        user_id: int,
        user_role: str
    ):

        restaurant = self.validate_restaurant(
            db,
            data.restaurant_id
        )

        # Normalize role
        user_role = user_role.upper()

        # --------------------------------------------------
        # ADMIN
        # --------------------------------------------------

        if user_role == "ADMIN":
            pass

        # --------------------------------------------------
        # RESTAURANT OWNER
        # --------------------------------------------------

        elif user_role == "RESTAURANT_OWNER":

            if restaurant.owner_id != user_id:
                raise HTTPException(
                    status_code=403,
                    detail=(
                        "You can modify only your "
                        "restaurant menu"
                    )
                )

        # --------------------------------------------------
        # RESTAURANT STAFF
        # --------------------------------------------------

        elif user_role == "RESTAURANT_STAFF":

            raise HTTPException(
                status_code=403,
                detail=(
                    "Restaurant staff must be assigned "
                    "to a restaurant"
                )
            )

        # --------------------------------------------------
        # OTHER USERS
        # --------------------------------------------------

        else:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission"
            )

        # --------------------------------------------------
        # Create Food Item
        # --------------------------------------------------

        food_item = FoodItem(
            restaurant_id=data.restaurant_id,
            category=data.category,
            name=data.name,
            description=data.description,
            price=data.price,
            preparation_time=data.preparation_time,
            availability=data.availability,
            vegetarian=data.vegetarian,
            spicy_level=data.spicy_level,
        )

        return self.repository.create(
            db,
            food_item
        )

    # ==================================================
    # Get Single Food Item
    # ==================================================

    def get_food_item(
        self,
        db: Session,
        food_item_id: int
    ):

        food_item = self.repository.get_by_id(
            db,
            food_item_id
        )

        if not food_item:
            raise HTTPException(
                status_code=404,
                detail="Food item not found"
            )

        return food_item

    # ==================================================
    # Get All Food Items
    # ==================================================

    def get_food_items(
        self,
        db: Session,
        restaurant_id: int | None = None
    ):

        return self.repository.get_all(
            db,
            restaurant_id
        )

    # ==================================================
    # Check Permission
    # ==================================================

    def check_permission(
        self,
        db: Session,
        food_item: FoodItem,
        user_id: int,
        user_role: str
    ):

        # Normalize role
        user_role = user_role.upper()

        # --------------------------------------------------
        # ADMIN can modify any food item
        # --------------------------------------------------

        if user_role == "ADMIN":
            return

        # --------------------------------------------------
        # Find Restaurant
        # --------------------------------------------------

        restaurant = self.validate_restaurant(
            db,
            food_item.restaurant_id
        )

        # --------------------------------------------------
        # RESTAURANT OWNER
        # --------------------------------------------------

        if user_role == "RESTAURANT_OWNER":

            if restaurant.owner_id != user_id:
                raise HTTPException(
                    status_code=403,
                    detail=(
                        "You can modify only your "
                        "restaurant menu"
                    )
                )

            return

        # --------------------------------------------------
        # RESTAURANT STAFF
        # --------------------------------------------------

        if user_role == "RESTAURANT_STAFF":

            raise HTTPException(
                status_code=403,
                detail=(
                    "Restaurant staff must be assigned "
                    "to a restaurant"
                )
            )

        # --------------------------------------------------
        # Other roles
        # --------------------------------------------------

        raise HTTPException(
            status_code=403,
            detail="You do not have permission"
        )

    # ==================================================
    # Update Food Item
    # ==================================================

    def update_food_item(
        self,
        db: Session,
        food_item_id: int,
        data: FoodItemUpdate,
        user_id: int,
        user_role: str
    ):

        food_item = self.get_food_item(
            db,
            food_item_id
        )

        self.check_permission(
            db,
            food_item,
            user_id,
            user_role
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():

            setattr(
                food_item,
                key,
                value
            )

        return self.repository.update(
            db,
            food_item
        )

    # ==================================================
    # Delete Food Item
    # ==================================================

    def delete_food_item(
        self,
        db: Session,
        food_item_id: int,
        user_id: int,
        user_role: str
    ):

        food_item = self.get_food_item(
            db,
            food_item_id
        )

        self.check_permission(
            db,
            food_item,
            user_id,
            user_role
        )

        self.repository.soft_delete(
            db,
            food_item
        )

        return {
            "message": "Food item deleted successfully"
        }

    # ==================================================
    # Search Food Items
    # ==================================================

    def search_food_items(
        self,
        db: Session,
        restaurant_id: int | None = None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        vegetarian: bool | None = None,
        spicy_level: int | None = None,
        availability: bool | None = None,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "name",
        sort_order: str = "asc"
    ):

        # --------------------------------------------------
        # Validate pagination
        # --------------------------------------------------

        if page < 1:
            page = 1

        if limit < 1:
            limit = 10

        if limit > 100:
            limit = 100

        # --------------------------------------------------
        # Validate price range
        # --------------------------------------------------

        if (
            min_price is not None
            and max_price is not None
            and min_price > max_price
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "min_price cannot be greater "
                    "than max_price"
                )
            )

        # --------------------------------------------------
        # Validate sorting
        # --------------------------------------------------

        allowed_sort_fields = {
            "name",
            "price",
            "preparation_time",
            "spicy_level",
            "created_at",
        }

        if sort_by not in allowed_sort_fields:
            sort_by = "name"

        sort_order = sort_order.lower()

        if sort_order not in {
            "asc",
            "desc"
        }:
            sort_order = "asc"

        # --------------------------------------------------
        # Search Repository
        # --------------------------------------------------

        items, total = (
            self.repository.search_food_items(
                db=db,
                restaurant_id=restaurant_id,
                category=category,
                min_price=min_price,
                max_price=max_price,
                vegetarian=vegetarian,
                spicy_level=spicy_level,
                availability=availability,
                page=page,
                limit=limit,
                sort_by=sort_by,
                sort_order=sort_order
            )
        )

        # --------------------------------------------------
        # Calculate Total Pages
        # --------------------------------------------------

        total_pages = (
            ceil(total / limit)
            if total > 0
            else 0
        )

        # --------------------------------------------------
        # Return Response
        # --------------------------------------------------

        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        }
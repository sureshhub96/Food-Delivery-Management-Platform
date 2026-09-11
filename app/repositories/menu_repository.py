from sqlalchemy.orm import Session

from app.models.menu import FoodItem


class MenuRepository:

    def create(
        self,
        db: Session,
        food_item: FoodItem
    ):
        db.add(food_item)
        db.commit()
        db.refresh(food_item)

        return food_item

    def get_by_id(
        self,
        db: Session,
        food_item_id: int
    ):
        return (
            db.query(FoodItem)
            .filter(
                FoodItem.id == food_item_id,
                FoodItem.is_deleted == False
            )
            .first()
        )

    def get_all(
        self,
        db: Session,
        restaurant_id: int | None = None
    ):
        query = (
            db.query(FoodItem)
            .filter(
                FoodItem.is_deleted == False
            )
        )

        if restaurant_id is not None:
            query = query.filter(
                FoodItem.restaurant_id == restaurant_id
            )

        return query.all()

    def update(
        self,
        db: Session,
        food_item: FoodItem
    ):
        db.commit()
        db.refresh(food_item)

        return food_item

    def soft_delete(
        self,
        db: Session,
        food_item: FoodItem
    ):
        food_item.is_deleted = True

        db.commit()
        db.refresh(food_item)

        return food_item

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
        # Base query
        query = (
            db.query(FoodItem)
            .filter(
                FoodItem.is_deleted == False
            )
        )

        # Restaurant filter
        if restaurant_id is not None:
            query = query.filter(
                FoodItem.restaurant_id == restaurant_id
            )

        # Category filter
        if category:
            query = query.filter(
                FoodItem.category.ilike(
                    f"%{category}%"
                )
            )

        # Minimum price
        if min_price is not None:
            query = query.filter(
                FoodItem.price >= min_price
            )

        # Maximum price
        if max_price is not None:
            query = query.filter(
                FoodItem.price <= max_price
            )

        # Vegetarian filter
        if vegetarian is not None:
            query = query.filter(
                FoodItem.vegetarian == vegetarian
            )

        # Spicy level filter
        if spicy_level is not None:
            query = query.filter(
                FoodItem.spicy_level == spicy_level
            )

        # Availability filter
        if availability is not None:
            query = query.filter(
                FoodItem.availability == availability
            )

        # Total count before pagination
        total = query.count()

        # Allowed sorting fields
        allowed_sort_fields = {
            "name": FoodItem.name,
            "price": FoodItem.price,
            "spicy_level": FoodItem.spicy_level,
            "created_at": FoodItem.created_at,
        }

        sort_column = allowed_sort_fields.get(
            sort_by,
            FoodItem.name
        )

        # Sorting
        if sort_order.lower() == "desc":
            query = query.order_by(
                sort_column.desc()
            )
        else:
            query = query.order_by(
                sort_column.asc()
            )

        # Pagination
        if page < 1:
            page = 1

        if limit < 1:
            limit = 10

        offset = (page - 1) * limit

        # Fetch paginated records
        items = (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )

        return items, total
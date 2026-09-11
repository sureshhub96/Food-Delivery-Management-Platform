from fastapi import HTTPException
from sqlalchemy.orm import Session
import math

from app.models.restaurant import Restaurant
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantUpdate,
)


class RestaurantService:

    def __init__(self):
        self.repository = RestaurantRepository()

    # =====================================================
    # CREATE RESTAURANT
    # =====================================================

    def create_restaurant(
        self,
        db: Session,
        data: RestaurantCreate,
        owner_id: int
    ):
        restaurant = Restaurant(
            restaurant_name=data.restaurant_name,
            owner_id=owner_id,
            address=data.address,
            city=data.city,
            phone=data.phone,
            cuisine_type=data.cuisine_type,
            opening_time=data.opening_time,
            closing_time=data.closing_time,
            status=data.status,
            delivery_radius=data.delivery_radius,
        )

        return self.repository.create(
            db,
            restaurant
        )

    # =====================================================
    # GET RESTAURANT BY ID
    # =====================================================

    def get_restaurant(
        self,
        db: Session,
        restaurant_id: int
    ):
        restaurant = self.repository.get_by_id(
            db,
            restaurant_id
        )

        if not restaurant:
            raise HTTPException(
                status_code=404,
                detail="Restaurant not found"
            )

        return restaurant

    # =====================================================
    # GET ALL RESTAURANTS
    # =====================================================

    def get_restaurants(
        self,
        db: Session
    ):
        return self.repository.get_all(db)

    # =====================================================
    # UPDATE RESTAURANT
    # =====================================================

    def update_restaurant(
        self,
        db: Session,
        restaurant_id: int,
        data: RestaurantUpdate,
        user_id: int,
        is_admin: bool = False
    ):
        restaurant = self.get_restaurant(
            db,
            restaurant_id
        )

        if not is_admin and restaurant.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You can update only your restaurant"
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        new_opening = update_data.get(
            "opening_time",
            restaurant.opening_time
        )

        new_closing = update_data.get(
            "closing_time",
            restaurant.closing_time
        )

        if new_opening and new_closing:
            if new_closing <= new_opening:
                raise HTTPException(
                    status_code=400,
                    detail="Closing time must be after opening time"
                )

        for key, value in update_data.items():
            setattr(
                restaurant,
                key,
                value
            )

        return self.repository.update(
            db,
            restaurant
        )

    # =====================================================
    # DELETE RESTAURANT
    # =====================================================

    def delete_restaurant(
        self,
        db: Session,
        restaurant_id: int,
        user_id: int,
        is_admin: bool = False
    ):
        restaurant = self.get_restaurant(
            db,
            restaurant_id
        )

        if not is_admin and restaurant.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You can delete only your restaurant"
            )

        return self.repository.soft_delete(
            db,
            restaurant
        )

    # =====================================================
    # SEARCH RESTAURANTS
    # =====================================================

    def search_restaurants(
        self,
        db: Session,
        city=None,
        cuisine_type=None,
        status=None,
        search=None,
        page=1,
        limit=10,
        sort_by="created_at",
        sort_order="desc"
    ):
        # Validate pagination
        if page < 1:
            page = 1

        if limit < 1:
            limit = 10

        if limit > 100:
            limit = 100

        # Allowed sorting fields
        allowed_sort_fields = {
            "created_at",
            "restaurant_name",
            "city",
            "delivery_radius"
        }

        if sort_by not in allowed_sort_fields:
            sort_by = "created_at"

        # Validate sort order
        sort_order = sort_order.lower()

        if sort_order not in {"asc", "desc"}:
            sort_order = "desc"

        # Normalize filters
        if city:
            city = city.strip()

        if cuisine_type:
            cuisine_type = cuisine_type.strip()

        if status:
            status = status.upper()

        if search:
            search = search.strip()

        # Repository search
        items, total = self.repository.search_restaurants(
            db=db,
            city=city,
            cuisine_type=cuisine_type,
            status=status,
            search=search,
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # Calculate total pages
        total_pages = (
            math.ceil(total / limit)
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
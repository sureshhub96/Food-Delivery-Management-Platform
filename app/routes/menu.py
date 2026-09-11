from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.menu import (
    FoodItemCreate,
    FoodItemResponse,
    FoodItemUpdate,
)
from app.services.menu_service import MenuService
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/menu",
    tags=["Menu"]
)

service = MenuService()


# =========================================================
# CREATE FOOD ITEM
# =========================================================

@router.post(
    "/items",
    response_model=FoodItemResponse,
    status_code=status.HTTP_201_CREATED
)
def create_food_item(
    data: FoodItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.create_food_item(
        db=db,
        data=data,
        user_id=current_user.id,
        user_role=current_user.role
    )


# =========================================================
# GET ALL FOOD ITEMS
# =========================================================

@router.get(
    "/items",
    response_model=list[FoodItemResponse]
)
def get_food_items(
    restaurant_id: int | None = None,
    db: Session = Depends(get_db)
):
    return service.get_food_items(
        db=db,
        restaurant_id=restaurant_id
    )


# =========================================================
# SEARCH FOOD ITEMS
# IMPORTANT: Keep /search before /items/{food_item_id}
# =========================================================

@router.get(
    "/items/search"
)
def search_food_items(
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
    sort_order: str = "asc",
    db: Session = Depends(get_db)
):
    return service.search_food_items(
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


# =========================================================
# GET FOOD ITEM BY ID
# =========================================================

@router.get(
    "/items/{food_item_id}",
    response_model=FoodItemResponse
)
def get_food_item(
    food_item_id: int,
    db: Session = Depends(get_db)
):
    return service.get_food_item(
        db=db,
        food_item_id=food_item_id
    )


# =========================================================
# UPDATE FOOD ITEM
# =========================================================

@router.put(
    "/items/{food_item_id}",
    response_model=FoodItemResponse
)
def update_food_item(
    food_item_id: int,
    data: FoodItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.update_food_item(
        db=db,
        food_item_id=food_item_id,
        data=data,
        user_id=current_user.id,
        user_role=current_user.role
    )


# =========================================================
# DELETE FOOD ITEM
# =========================================================

@router.delete(
    "/items/{food_item_id}"
)
def delete_food_item(
    food_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.delete_food_item(
        db=db,
        food_item_id=food_item_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
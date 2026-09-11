from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantResponse,
    RestaurantUpdate,
)
from app.services.restaurant_service import RestaurantService
from app.utils.dependencies import (
    get_current_user,
    require_roles,
)


router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"]
)

service = RestaurantService()


# =========================================================
# CREATE RESTAURANT
# =========================================================

@router.post(
    "",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED
)
def create_restaurant(
    data: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "RESTAURANT_OWNER"
        )
    )
):
    return service.create_restaurant(
        db,
        data,
        current_user.id
    )


# =========================================================
# GET ALL RESTAURANTS
# =========================================================

@router.get(
    "",
    response_model=list[RestaurantResponse]
)
def get_restaurants(
    db: Session = Depends(get_db)
):
    return service.get_restaurants(db)


# =========================================================
# SEARCH RESTAURANTS
# IMPORTANT: Keep this BEFORE /{restaurant_id}
# =========================================================

@router.get(
    "/search"
)
def search_restaurants(
    city: str | None = None,
    cuisine_type: str | None = None,
    status: str | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    return service.search_restaurants(
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


# =========================================================
# GET RESTAURANT BY ID
# =========================================================

@router.get(
    "/{restaurant_id}",
    response_model=RestaurantResponse
)
def get_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    return service.get_restaurant(
        db,
        restaurant_id
    )


# =========================================================
# UPDATE RESTAURANT
# =========================================================

@router.put(
    "/{restaurant_id}",
    response_model=RestaurantResponse
)
def update_restaurant(
    restaurant_id: int,
    data: RestaurantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return service.update_restaurant(
        db,
        restaurant_id,
        data,
        current_user.id,
        current_user.role == "ADMIN"
    )


# =========================================================
# DELETE RESTAURANT
# =========================================================

@router.delete(
    "/{restaurant_id}"
)
def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service.delete_restaurant(
        db,
        restaurant_id,
        current_user.id,
        current_user.role == "ADMIN"
    )

    return {
        "message": "Restaurant deleted successfully"
    }
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

from app.schemas.analytics import (
    RestaurantDashboardResponse,
    TopFoodItemResponse,
    OrderStatusSummaryResponse
)

from app.services.analytics_service import (
    analytics_service
)

from app.utils.dependencies import (
    get_current_user
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


def check_restaurant_access(
    db: Session,
    restaurant_id: int,
    current_user: User
):
    from app.models.restaurant import Restaurant

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

    if current_user.role == "ADMIN":
        return restaurant

    if (
        current_user.role == "RESTAURANT_OWNER"
        and restaurant.owner_id == current_user.id
    ):
        return restaurant

    raise HTTPException(
        status_code=403,
        detail="You do not have access to this restaurant"
    )


# --------------------------------------------------
# RESTAURANT DASHBOARD
# --------------------------------------------------

@router.get(
    "/restaurants/{restaurant_id}/dashboard",
    response_model=RestaurantDashboardResponse
)
def restaurant_dashboard(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_restaurant_access(
        db,
        restaurant_id,
        current_user
    )

    result = analytics_service.get_restaurant_dashboard(
        db,
        restaurant_id
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    return result


# --------------------------------------------------
# TOP FOOD ITEMS
# --------------------------------------------------

@router.get(
    "/restaurants/{restaurant_id}/top-foods",
    response_model=list[TopFoodItemResponse]
)
def top_food_items(
    restaurant_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_restaurant_access(
        db,
        restaurant_id,
        current_user
    )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    return analytics_service.get_top_food_items(
        db,
        restaurant_id,
        limit
    )


# --------------------------------------------------
# ORDER STATUS SUMMARY
# --------------------------------------------------

@router.get(
    "/restaurants/{restaurant_id}/order-status",
    response_model=list[OrderStatusSummaryResponse]
)
def order_status_summary(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_restaurant_access(
        db,
        restaurant_id,
        current_user
    )

    return analytics_service.get_order_status_summary(
        db,
        restaurant_id
    )
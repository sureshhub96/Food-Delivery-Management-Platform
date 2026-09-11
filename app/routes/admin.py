from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

from app.schemas.analytics import (
    AdminDashboardResponse,
    MonthlyOrderResponse,
    MonthlyRevenueResponse
)

from app.services.analytics_service import (
    analytics_service
)

from app.utils.dependencies import (
    get_current_user
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin Analytics"]
)


def require_admin(
    current_user: User
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse
)
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)

    return analytics_service.get_admin_dashboard(
        db
    )


# --------------------------------------------------
# MONTHLY ORDERS
# --------------------------------------------------

@router.get(
    "/analytics/monthly-orders",
    response_model=list[MonthlyOrderResponse]
)
def monthly_orders(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)

    if year < 2000 or year > 2100:
        raise HTTPException(
            status_code=400,
            detail="Invalid year"
        )

    return analytics_service.get_monthly_orders(
        db,
        year
    )


# --------------------------------------------------
# MONTHLY REVENUE
# --------------------------------------------------

@router.get(
    "/analytics/monthly-revenue",
    response_model=list[MonthlyRevenueResponse]
)
def monthly_revenue(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)

    if year < 2000 or year > 2100:
        raise HTTPException(
            status_code=400,
            detail="Invalid year"
        )

    return analytics_service.get_monthly_revenue(
        db,
        year
    )
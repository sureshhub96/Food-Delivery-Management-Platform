from pydantic import BaseModel


class RestaurantDashboardResponse(BaseModel):
    restaurant_id: int

    total_orders: int
    delivered_orders: int
    cancelled_orders: int
    pending_orders: int

    total_revenue: float
    average_order_value: float

    top_foods: list
    order_status_summary: dict


class TopFoodItemResponse(BaseModel):
    food_item_id: int
    food_name: str
    quantity_sold: int
    revenue: float


class OrderStatusSummaryResponse(BaseModel):
    pending: int = 0
    accepted: int = 0
    preparing: int = 0
    ready: int = 0
    picked_up: int = 0
    out_for_delivery: int = 0
    delivered: int = 0
    cancelled: int = 0


class AdminDashboardResponse(BaseModel):
    total_users: int
    total_customers: int
    total_restaurants: int
    total_delivery_partners: int

    total_orders: int
    delivered_orders: int
    cancelled_orders: int
    pending_orders: int

    total_revenue: float
    successful_payments: float
    total_refunds: float


class MonthlyOrderResponse(BaseModel):
    month: str
    order_count: int


class MonthlyRevenueResponse(BaseModel):
    month: str
    revenue: float
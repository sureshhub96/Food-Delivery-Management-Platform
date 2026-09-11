from fastapi import FastAPI

from app.database import Base, engine

# Models
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.menu import FoodItem
from app.models.customer import Customer
from app.models.address import Address
from app.models.cart import Cart, CartItem
from app.models.coupon import Coupon
from app.models.order import Order, OrderItem
from app.models.delivery import DeliveryPartner
from app.models.tracking import OrderTracking
from app.models.payment import Payment
from app.models.refund import Refund
from app.models.review import Review
from app.models.notification import Notification

# Routes
from app.routes.auth import router as auth_router
from app.routes.restaurants import router as restaurants_router
from app.routes.menu import router as menu_router
from app.routes.customers import router as customers_router
from app.routes.cart import router as cart_router
from app.routes.coupons import router as coupons_router
from app.routes.orders import router as orders_router
from app.routes.delivery import router as delivery_router
from app.routes.tracking import router as tracking_router
from app.routes.payments import router as payments_router
from app.routes.refunds import router as refunds_router
from app.routes.reviews import router as reviews_router
from app.routes.analytics import router as analytics_router
from app.routes.admin import router as admin_router
from app.routes.notifications import router as notifications_router


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Restaurant & Food Delivery Management System",
    description="Complete Food Delivery Management Platform using FastAPI",
    version="1.0.0"
)


# --------------------------------------------------
# Database
# --------------------------------------------------
# Temporary for development.
# Once Alembic is fully configured, remove this line
# and use: alembic upgrade head

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# Routers
# --------------------------------------------------

app.include_router(auth_router)
app.include_router(restaurants_router)
app.include_router(menu_router)
app.include_router(customers_router)
app.include_router(cart_router)
app.include_router(coupons_router)
app.include_router(orders_router)
app.include_router(delivery_router)
app.include_router(tracking_router)
app.include_router(payments_router)
app.include_router(refunds_router)
app.include_router(reviews_router)
app.include_router(analytics_router)
app.include_router(admin_router)
app.include_router(notifications_router)


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Restaurant & Food Delivery Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
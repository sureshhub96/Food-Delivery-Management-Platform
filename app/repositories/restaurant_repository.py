from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant


class RestaurantRepository:

    def create(
        self,
        db: Session,
        restaurant: Restaurant
    ):
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)

        return restaurant

    def get_by_id(
        self,
        db: Session,
        restaurant_id: int
    ):
        return db.query(Restaurant).filter(
            Restaurant.id == restaurant_id,
            Restaurant.is_deleted == False
        ).first()

    def get_all(
        self,
        db: Session
    ):
        return db.query(Restaurant).filter(
            Restaurant.is_deleted == False
        ).all()

    def update(
        self,
        db: Session,
        restaurant: Restaurant
    ):
        db.commit()
        db.refresh(restaurant)

        return restaurant

    def soft_delete(
        self,
        db: Session,
        restaurant: Restaurant
    ):
        restaurant.is_deleted = True

        db.commit()

        return restaurant
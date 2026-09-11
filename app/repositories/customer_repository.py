from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:

    def create(
        self,
        db: Session,
        customer: Customer
    ):
        db.add(customer)
        db.commit()
        db.refresh(customer)

        return customer

    def get_by_id(
        self,
        db: Session,
        customer_id: int
    ):
        return db.query(Customer).filter(
            Customer.id == customer_id
        ).first()

    def get_by_user_id(
        self,
        db: Session,
        user_id: int
    ):
        return db.query(Customer).filter(
            Customer.user_id == user_id
        ).first()
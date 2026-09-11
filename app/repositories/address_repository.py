from sqlalchemy.orm import Session

from app.models.address import Address


class AddressRepository:

    def create(
        self,
        db: Session,
        address: Address
    ):
        db.add(address)
        db.commit()
        db.refresh(address)

        return address

    def get_by_id(
        self,
        db: Session,
        address_id: int
    ):
        return db.query(Address).filter(
            Address.id == address_id
        ).first()

    def get_customer_addresses(
        self,
        db: Session,
        customer_id: int
    ):
        return db.query(Address).filter(
            Address.customer_id == customer_id
        ).all()

    def get_default_address(
        self,
        db: Session,
        customer_id: int
    ):
        return db.query(Address).filter(
            Address.customer_id == customer_id,
            Address.is_default == True
        ).first()

    def update(
        self,
        db: Session,
        address: Address
    ):
        db.commit()
        db.refresh(address)

        return address
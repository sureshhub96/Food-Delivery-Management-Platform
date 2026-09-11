from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.address import Address
from app.models.customer import Customer
from app.models.user import User

from app.repositories.address_repository import (
    AddressRepository,
)
from app.repositories.customer_repository import (
    CustomerRepository,
)

from app.schemas.address import (
    AddressCreate,
    AddressUpdate,
)
from app.schemas.customer import CustomerCreate


class CustomerService:

    def __init__(self):
        self.customer_repository = CustomerRepository()
        self.address_repository = AddressRepository()

    def create_customer(
        self,
        db: Session,
        data: CustomerCreate,
        user_id: int
    ):

        existing = (
            self.customer_repository.get_by_user_id(
                db,
                user_id
            )
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Customer profile already exists"
            )

        customer = Customer(
            user_id=user_id
        )

        return self.customer_repository.create(
            db,
            customer
        )

    def get_customer(
        self,
        db: Session,
        customer_id: int
    ):

        customer = (
            self.customer_repository.get_by_id(
                db,
                customer_id
            )
        )

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        return customer

    def verify_customer_access(
        self,
        customer: Customer,
        current_user: User
    ):

        if (
            current_user.role != "ADMIN"
            and customer.user_id != current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You cannot access this customer"
            )

    def create_address(
        self,
        db: Session,
        customer_id: int,
        data: AddressCreate,
        current_user: User
    ):

        customer = self.get_customer(
            db,
            customer_id
        )

        self.verify_customer_access(
            customer,
            current_user
        )

        existing_addresses = (
            self.address_repository
            .get_customer_addresses(
                db,
                customer_id
            )
        )

        # First address automatically becomes default
        if not existing_addresses:
            data.is_default = True

        # If this address is default,
        # remove default from previous address
        if data.is_default:

            current_default = (
                self.address_repository
                .get_default_address(
                    db,
                    customer_id
                )
            )

            if current_default:
                current_default.is_default = False

        address = Address(
            customer_id=customer_id,
            address_line=data.address_line,
            city=data.city,
            pincode=data.pincode,
            latitude=data.latitude,
            longitude=data.longitude,
            address_type=data.address_type.upper(),
            is_default=data.is_default,
        )

        return self.address_repository.create(
            db,
            address
        )

    def get_addresses(
        self,
        db: Session,
        customer_id: int,
        current_user: User
    ):

        customer = self.get_customer(
            db,
            customer_id
        )

        self.verify_customer_access(
            customer,
            current_user
        )

        return (
            self.address_repository
            .get_customer_addresses(
                db,
                customer_id
            )
        )

    def update_address(
        self,
        db: Session,
        address_id: int,
        data: AddressUpdate,
        current_user: User
    ):

        address = (
            self.address_repository
            .get_by_id(
                db,
                address_id
            )
        )

        if not address:
            raise HTTPException(
                status_code=404,
                detail="Address not found"
            )

        customer = self.get_customer(
            db,
            address.customer_id
        )

        self.verify_customer_access(
            customer,
            current_user
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if update_data.get("is_default") is True:

            current_default = (
                self.address_repository
                .get_default_address(
                    db,
                    address.customer_id
                )
            )

            if (
                current_default
                and current_default.id != address.id
            ):
                current_default.is_default = False

        if "address_type" in update_data:
            update_data["address_type"] = (
                update_data["address_type"].upper()
            )

        for key, value in update_data.items():
            setattr(
                address,
                key,
                value
            )

        return self.address_repository.update(
            db,
            address
        )
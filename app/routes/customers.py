from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

from app.schemas.address import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
)

from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
)

from app.services.customer_service import (
    CustomerService,
)

from app.utils.dependencies import (
    get_current_user,
)


router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)

service = CustomerService()


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return service.create_customer(
        db,
        data,
        current_user.id
    )


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    customer = service.get_customer(
        db,
        customer_id
    )

    service.verify_customer_access(
        customer,
        current_user
    )

    return customer


@router.post(
    "/{customer_id}/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED
)
def create_address(
    customer_id: int,
    data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return service.create_address(
        db,
        customer_id,
        data,
        current_user
    )


@router.get(
    "/{customer_id}/addresses",
    response_model=list[AddressResponse]
)
def get_addresses(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return service.get_addresses(
        db,
        customer_id,
        current_user
    )


@router.put(
    "/addresses/{address_id}",
    response_model=AddressResponse
)
def update_address(
    address_id: int,
    data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return service.update_address(
        db,
        address_id,
        data,
        current_user
    )
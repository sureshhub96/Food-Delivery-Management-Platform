from pydantic import BaseModel, Field


class AddressCreate(BaseModel):

    address_line: str = Field(
        ...,
        min_length=5,
        max_length=255
    )

    city: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    pincode: str = Field(
        ...,
        min_length=4,
        max_length=10
    )

    latitude: float | None = None

    longitude: float | None = None

    address_type: str = "HOME"

    is_default: bool = False


class AddressUpdate(BaseModel):

    address_line: str | None = None

    city: str | None = None

    pincode: str | None = None

    latitude: float | None = None

    longitude: float | None = None

    address_type: str | None = None

    is_default: bool | None = None


class AddressResponse(BaseModel):

    id: int
    customer_id: int
    address_line: str
    city: str
    pincode: str
    latitude: float | None
    longitude: float | None
    address_type: str
    is_default: bool

    model_config = {
        "from_attributes": True
    }
from typing import Optional

from pydantic import BaseModel, Field


class DeliveryPartnerCreate(BaseModel):
    user_id: int

    name: str = Field(
        min_length=2,
        max_length=100
    )

    phone: str = Field(
        min_length=10,
        max_length=20
    )

    vehicle_type: str = Field(
        min_length=2,
        max_length=50
    )

    vehicle_number: str = Field(
        min_length=3,
        max_length=50
    )


class DeliveryPartnerUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    phone: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=20
    )

    vehicle_type: Optional[str] = None

    vehicle_number: Optional[str] = None

    availability_status: Optional[str] = None

    current_latitude: Optional[float] = None

    current_longitude: Optional[float] = None

    is_active: Optional[bool] = None


class DeliveryPartnerResponse(BaseModel):
    id: int
    user_id: int
    name: str
    phone: str
    vehicle_type: str
    vehicle_number: str
    availability_status: str

    current_latitude: Optional[float]
    current_longitude: Optional[float]

    is_active: bool

    class Config:
        from_attributes = True


class DeliveryStatusUpdate(BaseModel):
    availability_status: str


class AssignDeliveryRequest(BaseModel):
    delivery_partner_id: int
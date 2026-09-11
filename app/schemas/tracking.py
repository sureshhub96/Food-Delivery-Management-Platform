from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TrackingCreate(BaseModel):
    status: str

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    remarks: Optional[str] = Field(
        default=None,
        max_length=500
    )


class TrackingResponse(BaseModel):
    id: int
    order_id: int
    status: str
    latitude: Optional[float]
    longitude: Optional[float]
    remarks: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
    remarks: Optional[str] = Field(
        default=None,
        max_length=500
    )
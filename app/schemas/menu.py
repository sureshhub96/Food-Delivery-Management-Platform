from pydantic import BaseModel, Field, field_validator


class FoodItemCreate(BaseModel):

    restaurant_id: int

    category: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    description: str | None = None

    price: float = Field(
        ...,
        gt=0
    )

    preparation_time: int = Field(
        ...,
        gt=0
    )

    availability: bool = True

    vegetarian: bool = False

    spicy_level: int = Field(
        default=0,
        ge=0,
        le=5
    )


class FoodItemUpdate(BaseModel):

    category: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    description: str | None = None

    price: float | None = Field(
        default=None,
        gt=0
    )

    preparation_time: int | None = Field(
        default=None,
        gt=0
    )

    availability: bool | None = None

    vegetarian: bool | None = None

    spicy_level: int | None = Field(
        default=None,
        ge=0,
        le=5
    )


class FoodItemResponse(BaseModel):

    id: int
    restaurant_id: int
    category: str
    name: str
    description: str | None
    price: float
    preparation_time: int
    availability: bool
    vegetarian: bool
    spicy_level: int
    is_deleted: bool

    model_config = {
        "from_attributes": True
    }
from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: str

    phone: str = Field(
        ...,
        min_length=10,
        max_length=20
    )


class CustomerResponse(BaseModel):

    id: int
    user_id: int

    model_config = {
        "from_attributes": True
    }
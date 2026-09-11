from pydantic import BaseModel, EmailStr, Field


# =========================================================
# REGISTER
# =========================================================

class RegisterRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr

    phone: str | None = Field(
        default=None,
        max_length=15
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=72
    )

    role: str = Field(
        default="CUSTOMER"
    )


# =========================================================
# LOGIN
# =========================================================

class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=72
    )


# =========================================================
# TOKEN RESPONSE
# =========================================================

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# =========================================================
# REFRESH TOKEN
# =========================================================

class RefreshRequest(BaseModel):
    refresh_token: str


# =========================================================
# USER RESPONSE
# =========================================================

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None = None
    role: str
    is_active: bool

    class Config:
        from_attributes = True


# =========================================================
# CHANGE PASSWORD
# =========================================================

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(
        ...,
        min_length=8,
        max_length=72
    )

    new_password: str = Field(
        ...,
        min_length=8,
        max_length=72
    )
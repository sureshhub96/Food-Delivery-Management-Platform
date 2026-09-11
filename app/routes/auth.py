from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

from app.schemas.auth import (
    ChangePasswordRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

from app.utils.dependencies import get_current_user

from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================================================
# REGISTER
# =========================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    # -----------------------------------------------------
    # Allowed roles for public registration
    # ADMIN is NOT allowed through public registration
    # -----------------------------------------------------

    allowed_roles = {
        "CUSTOMER",
        "RESTAURANT_OWNER",
        "DELIVERY_PARTNER"
    }

    # -----------------------------------------------------
    # Validate role
    # -----------------------------------------------------

    role = data.role.upper()

    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid role. Allowed roles are: "
                "CUSTOMER, RESTAURANT_OWNER, DELIVERY_PARTNER"
            )
        )

    # -----------------------------------------------------
    # Check email already exists
    # -----------------------------------------------------

    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # -----------------------------------------------------
    # Check phone already exists
    # -----------------------------------------------------

    if data.phone:

        existing_phone = db.query(User).filter(
            User.phone == data.phone
        ).first()

        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

    # -----------------------------------------------------
    # Create user
    # -----------------------------------------------------

    try:

        user = User(
            name=data.name,
            email=data.email,
            phone=data.phone,
            hashed_password=hash_password(data.password),
            role=role,
            is_active=True
        )

        db.add(user)

        db.commit()

        db.refresh(user)

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create user: {str(e)}"
        )

    return user


# =========================================================
# LOGIN
# OAuth2 Password Flow
# =========================================================

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Swagger OAuth2 sends:
    #
    # username = email
    # password = password
    # -----------------------------------------------------

    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    # -----------------------------------------------------
    # User not found
    # -----------------------------------------------------

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # -----------------------------------------------------
    # Verify password
    # -----------------------------------------------------

    if not verify_password(
        form_data.password,
        user.hashed_password
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # -----------------------------------------------------
    # Check account status
    # -----------------------------------------------------

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # -----------------------------------------------------
    # Create access token
    # -----------------------------------------------------

    access_token = create_access_token(
        user.id
    )

    # -----------------------------------------------------
    # Create refresh token
    # -----------------------------------------------------

    refresh_token = create_refresh_token(
        user.id
    )

    # -----------------------------------------------------
    # Return tokens
    # -----------------------------------------------------

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# =========================================================
# REFRESH TOKEN
# =========================================================

@router.post(
    "/refresh",
    response_model=TokenResponse
)
def refresh_token(
    data: RefreshRequest,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Decode refresh token
    # -----------------------------------------------------

    try:

        payload = decode_token(
            data.refresh_token
        )

        # -------------------------------------------------
        # Verify token type
        # -------------------------------------------------

        if payload.get("type") != "refresh":

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # -------------------------------------------------
        # Get user ID
        # -------------------------------------------------

        user_id = payload.get("sub")

        if not user_id:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

    except HTTPException:

        raise

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # -----------------------------------------------------
    # Convert user ID to integer
    # -----------------------------------------------------

    try:

        user_id = int(user_id)

    except (TypeError, ValueError):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )

    # -----------------------------------------------------
    # Find user
    # -----------------------------------------------------

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # -----------------------------------------------------
    # Check active status
    # -----------------------------------------------------

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )

    # -----------------------------------------------------
    # Generate new tokens
    # -----------------------------------------------------

    access_token = create_access_token(
        user.id
    )

    refresh_token = create_refresh_token(
        user.id
    )

    # -----------------------------------------------------
    # Return tokens
    # -----------------------------------------------------

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# =========================================================
# CURRENT USER
# =========================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):

    return current_user


# =========================================================
# CHANGE PASSWORD
# =========================================================

@router.put(
    "/change-password"
)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Verify current password
    # -----------------------------------------------------

    if not verify_password(
        data.current_password,
        current_user.hashed_password
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # -----------------------------------------------------
    # Make sure new password is different
    # -----------------------------------------------------

    if verify_password(
        data.new_password,
        current_user.hashed_password
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    # -----------------------------------------------------
    # Hash new password
    # -----------------------------------------------------

    current_user.hashed_password = hash_password(
        data.new_password
    )

    # -----------------------------------------------------
    # Save password
    # -----------------------------------------------------

    try:

        db.commit()

        db.refresh(current_user)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to change password"
        )

    return {
        "message": "Password changed successfully"
    }
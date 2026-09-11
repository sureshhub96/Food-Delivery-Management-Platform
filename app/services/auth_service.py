from datetime import datetime, timedelta, timezone
 
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
 
from app.models.user import User
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
 
 
class AuthService:
 
    def register(
        self,
        db: Session,
        name: str,
        email: str,
        phone: str | None,
        password: str,
        role: str = "CUSTOMER",
    ):
        existing_email = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )
 
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
 
        if phone:
            existing_phone = (
                db.query(User)
                .filter(User.phone == phone)
                .first()
            )
 
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already registered",
                )
 
        user = User(
            name=name,
            email=email,
            phone=phone,
            hashed_password=hash_password(password),
            role=role.upper(),
            is_active=True,
        )
 
        db.add(user)
        db.commit()
        db.refresh(user)
 
        return user
 
    def login(
        self,
        db: Session,
        email: str,
        password: str,
    ):
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )
 
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
 
        if not verify_password(
            password,
            user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
 
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
 
        access_token = create_access_token(
            {"sub": str(user.id), "role": user.role}
        )
 
        refresh_token = create_refresh_token(
            {"sub": str(user.id)}
        )
 
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
 
    def get_current_user(
        self,
        db: Session,
        user_id: int,
    ):
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )
 
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
 
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
 
        return user
 
    def change_password(
        self,
        db: Session,
        user: User,
        current_password: str,
        new_password: str,
    ):
        if not verify_password(
            current_password,
            user.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )
 
        user.hashed_password = hash_password(new_password)
 
        db.commit()
 
        return {
            "message": "Password changed successfully"
        }
 
 
auth_service = AuthService()
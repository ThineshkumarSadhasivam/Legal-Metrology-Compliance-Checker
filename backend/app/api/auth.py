from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    get_current_user
)

from app.models.user import User

from app.schemas.auth import (
    LoginRequest,
    LoginResponse
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(
            User.officer_id == payload.officer_id
        )
        .first()
    )

    if not user or not verify_password(
        payload.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Officer ID or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Officer account is inactive"
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "officer_id": user.officer_id,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "officer_id": user.officer_id,
        "role": user.role
    }


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "officer_id": current_user.officer_id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active
    }
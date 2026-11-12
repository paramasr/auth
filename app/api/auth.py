from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import SignupRequest, UserResponse, LoginRequest, RefreshRequest, TokenResponse, ForgotPasswordRequest, MessageResponse
from app.services.auth_service import (
    register_user,
    login_user,
    UserAlreadyExists
)

from app.services.refresh_token_service import (
    rotate_refresh_token,
    InvalidRefreshToken,
    RefreshTokenReuseDetected
)
from app.core.jwt import create_access_token
from app.services.refresh_token_service import create_refresh_token
from app.services.password_reset_service import request_password_reset

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def signup(
    signup_data: SignupRequest,
    db: Session = Depends(get_db)
):
    try:
        user = register_user(db, signup_data)
        return user
    except UserAlreadyExists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = login_user(db, login_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(db, str(user.id))
    db.commit()

    return TokenResponse(access_token=token, refresh_token=refresh_token)

@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)

def refresh(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    try:
        user_id, new_token = rotate_refresh_token(db, request.refresh_token)
        access_token = create_access_token(str(user_id))

        response = TokenResponse(
            access_token = access_token,
            refresh_token=new_token
        )

        return response

    except InvalidRefreshToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    except RefreshTokenReuseDetected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token reuse detected"
        )

@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK
)

def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    try:
        new_token = request_password_reset(db, str(request.email))

        _=new_token
        db.commit()

    except Exception:
        db.rollback()
        raise

    return MessageResponse(
        message=("If an account exists for this email, "
            "password reset instructions will be sent.")
    )
    

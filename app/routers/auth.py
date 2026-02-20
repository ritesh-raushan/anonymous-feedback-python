from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from typing import Annotated
from passlib.context import CryptContext

from app.database import get_db
from app.models.model import User

from app.schemas.user_schema import UserCreate, UserLogin, UserResponse, LoginResponse, UserResponse
from app.utils.tokens import (
    create_verification_token, 
    verify_verification_token,
    create_access_token,
    create_refresh_token
)
from app.utils.email_service import email_service

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=dict)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exixts
    existing_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")
    
    verification_token = create_verification_token(user.email)

    # Create new user
    new_user = User(
        username=user.username,
        email=user.email,
        password = pwd_context.hash(user.password),
        verification_token = verification_token,
        is_verified=False,
        is_accepting_messages=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send the VErfification Mail
    try:
        await email_service.send_verification_email(
            email=new_user.email,
            username=new_user.username,
            verification_token=verification_token
        )
    except Exception as e:
        # Log error but don't fail registration
        print(f"Error sending verification email: {e}")
    
    return {
        "message": "User registered successfully. Please check your email to verify your account.",
        "username": new_user.username,
        "email": new_user.email
    }

@router.get("/verify-email", status_code=status.HTTP_200_OK, response_model=dict)
async def verify_email(token: str, db: Session = Depends(get_db)):
    email = verify_verification_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.is_verified:
        return {"message": "Email already verified"}
    
    # Validate token matches the one stored in database
    if user.verification_token != token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")
    
    # Update user
    user.is_verified = True
    user.verification_token = None
    db.commit()

    # Send welcome email
    try:
        await email_service.send_welcome_email(
            email=user.email,
            username=user.username
        )
    except Exception as e:
        print(f"Error sending welcome email: {e}")
    
    return {"message": "Email verified successfully"}

@router.post("/login", response_model=LoginResponse)
async def login(user_credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not pwd_context.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )
    
    # Create access and refresh tokens
    access_token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": user.email, "user_id": str(user.id)})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )
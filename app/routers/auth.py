from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import Annotated
from passlib.context import CryptContext

from app.database import get_db
from app.models.model import User

from app.schemas.user_schema import UserCreate
from app.utils.tokens import create_verification_token, email_service

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
        verification_token = verification_token
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
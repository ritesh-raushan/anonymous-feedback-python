from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.models.model import User, Message
from app.schemas.message_schema import (
    MessageCreate,
    MessageResponse,
    PublicProfileResponse,
    DashboardResponse,
)
from app.schemas.user_schema import UserResponse
from app.utils import get_current_verified_user
from app.config import settings


router = APIRouter(tags=["Feedback"])

@router.post("/u/{username}", status_code=status.HTTP_201_CREATED, response_model=dict)
async def submit_feedback(
    username: str,
    message_data: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Submit anonymous feedback to a user.
    
    Anyone can submit feedback if the user accepts messages.
    """
    # Find recipient
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user accepts messages
    if not user.is_accepting_messages:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user is not accepting feedback at the moment"
        )
    
    # Create message
    new_message = Message(
        recipient_id=user.id,
        content=message_data.content
    )
    
    db.add(new_message)
    db.commit()
    
    return {
        "message": "Feedback submitted successfully",
        "success": True
    }
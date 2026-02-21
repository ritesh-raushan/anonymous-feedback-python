from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
import logging

from app.database import get_db
from app.models.model import User, Message
from app.schemas.message_schema import MessageCreate, MessageAcceptanceToggle
from app.utils.auth import get_current_verified_user
from app.schemas.user_schema import UserResponse

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Feedback"])

@router.post("/u/{username}", status_code=status.HTTP_201_CREATED, response_model=dict)
async def submit_feedback(username: str, message_data: MessageCreate, db: Session = Depends(get_db)):
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
    
    logger.info(f"Feedback submitted to user {user.username}")
    
    return {
        "message": "Feedback submitted successfully",
        "success": True
    }

@router.patch("/toggle-messages", response_model=UserResponse)
async def toggle_message_acceptance(
    toggle_data: MessageAcceptanceToggle,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Session = Depends(get_db)
):
    current_user.is_accepting_messages = toggle_data.is_accepting_messages
    db.commit()
    db.refresh(current_user)
    
    return current_user
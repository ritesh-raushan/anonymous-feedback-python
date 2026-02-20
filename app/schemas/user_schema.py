from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$', description="Username must contain 3-20 alphanumeric characters or underscores")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters long")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., min_length=6, description="Password")

class UserResponse(BaseModel):
    """Schema for user response."""
    id: uuid.UUID
    username: str
    email: EmailStr
    is_verified: bool
    is_accepting_messages: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LoginResponse(BaseModel):
    """Schema for login response."""
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="Message content upto characters")
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.config import settings

def create_verification_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.verification_token_expire_hours)
    to_encode = {"sub": email, "exp": expire, "type": "verification"}
    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return token


import random
import string
from datetime import datetime, timedelta
from typing import Callable

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address

from core.config import settings


limiter = Limiter(key_func=get_remote_address)


bearer_scheme = HTTPBearer()



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:

    @staticmethod
    def hash_password(plain_password: str) -> str:
        return pwd_context.hash(plain_password)

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        if not password_hash:
            return False
        return pwd_context.verify(plain_password, password_hash)

    @staticmethod
    def validate_password_strength(password: str) -> None:
      
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")



class TokenSecurityService:

    @staticmethod
    def generate_six_digit_code() -> str:
        return "".join(random.choices(string.digits, k=6))

    @staticmethod
    def generate_url_safe_token() -> str:
       
        import secrets
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_session_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.SESSION_TOKEN_MINUTES)
        to_encode.update({"exp": expire, "type": "session"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def build_token_payload(user) -> dict:
      
        return {
            "user_id": user.user_id,
            "role": user.role,
            "email": user.email,
            "facility_id": user.facility_id,
        }


def validate_secure_session(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = credentials.credentials  

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get("type") != "session":
            raise HTTPException(status_code=401, detail="Invalid token type: session token required.")

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Access Denied: Invalid or expired token.")



def require_role(*allowed_roles: str) -> Callable:

    def role_checker(token_data: dict = Depends(validate_secure_session)) -> dict:
        if token_data.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: requires one of roles {list(allowed_roles)}."
            )
        return token_data
    return role_checker



def enforce_facility_scope(resource_facility_id, token_data: dict) -> None:
   
    if token_data.get("role") == "Admin":
        return
    if resource_facility_id != token_data.get("facility_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: this record does not belong to your facility."
        )
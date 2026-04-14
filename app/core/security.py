from datetime import datetime, timedelta, timezone
from typing import Any, Union
from passlib.context import CryptContext
from jwt.exceptions import PyJWTError
import jwt
import uuid

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# hashing passwords
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# verifying passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# generating JWT tokens
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    jti = str(uuid.uuid4())

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "jti": jti,  # for blacklisting tokens on logout
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt



# decoding JWT tokens
def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except PyJWTError:
        return None
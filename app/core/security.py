from datetime import datetime, timedelta, timezone
from typing import Any, Union
from passlib.context import CryptContext
from jwt.exceptions import PyJWTError
import jwt
import uuid

from app.core.config import settings
from app.modules.auth.blacklist import add, exists

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# hashing passwords
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# verifying passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# generating JWT access tokens
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



# generating JWT refresh tokens
def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS) # 7 days

    jti = str(uuid.uuid4())

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "jti": jti,
        "type": "refresh" # to differentiate from access tokens
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


# generating JWT email verification tokens
def create_password_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "password",
        "jti": str(uuid.uuid4())
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt



# generating JWT reset password email tokens
def create_verification_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "verification",
        "jti": str(uuid.uuid4())
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt



# decoding JWT tokens
def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        jti = payload.get("jti")
        
        if jti and exists(jti): # verifying blacklist
            return None
            
        return payload
        
    except PyJWTError:
        return None
    


# Helper function to invalidate tokens by adding their jti to the blacklist
def invalidate_payload(payload: dict | None):
    if not payload:
        return
        
    jti = payload.get("jti")
    exp = payload.get("exp")
    
    if jti and exp:
        now = datetime.now(timezone.utc)
        expire_time = datetime.fromtimestamp(exp, tz=timezone.utc)
        expires_in = int((expire_time - now).total_seconds())
        if expires_in > 0:
            add(jti, expires_in)
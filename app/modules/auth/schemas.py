from pydantic import BaseModel, EmailStr, Field
import uuid
from datetime import datetime

from app.models.enums import UserTypeEnum

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    user_type: UserTypeEnum
    profile_picture_url: str | None = None
    is_verified: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str | None = None

class ResendEmailRequest(BaseModel):
    email: EmailStr

class UserResetPassword(BaseModel):
    token: str
    new_password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    user_type: UserTypeEnum
    profile_picture_url: str | None
    created_at: datetime
    class Config:
        from_attributes = True
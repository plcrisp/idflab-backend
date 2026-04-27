from pydantic import BaseModel, EmailStr, Field
import uuid

from app.models.enums import UserTypeEnum

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    user_type: UserTypeEnum
    profile_picture_url: str | None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    user_type: UserTypeEnum
    profile_picture_url: str | None
    class Config:
        from_attributes = True
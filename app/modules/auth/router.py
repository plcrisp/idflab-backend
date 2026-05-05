from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.session import get_db
from app.models.user import User
from app.modules.auth import schemas, service
from app.modules.auth.deps import get_current_user

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user_in: schemas.UserRegister, db: Session = Depends(get_db)):
    return service.register_user(db, user_in)

@router.post("/login", response_model=schemas.Token)
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    return service.authenticate_user(db, user_in)

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/refresh", response_model=schemas.Token)
def refresh_access_token(token_req: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    return service.refresh_token(db, token_req.refresh_token)

@router.post("/logout")
def logout(logout_req: schemas.LogoutRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    return service.logout_user(access_token=credentials.credentials, refresh_token=logout_req.refresh_token)

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    return service.verify_user_email(db, token)

@router.post("/resend-verification-email")
def resend_email(request: schemas.ResendEmailRequest,db: Session = Depends(get_db)):
    return service.resend_email_verification(db=db, user_email=request.email)

@router.post("/send-password-reset-email")
def send_password_email(request: schemas.ResendEmailRequest,db: Session = Depends(get_db)):
    return service.send_reset_password_email(db=db, user_email=request.email)

@router.post("/reset-password")
def password_reset(request: schemas.UserResetPassword,db: Session = Depends(get_db)):
    return service.reset_password(db=db, user_reset_password=request)
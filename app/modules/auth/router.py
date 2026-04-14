from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.modules.auth import schemas, service
from app.modules.auth.deps import get_current_user

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user_in: schemas.UserRegister, db: Session = Depends(get_db)):
    return service.register_user(db, user_in)

@router.post("/login", response_model=schemas.Token)
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    return service.authenticate_user(db, user_in)

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
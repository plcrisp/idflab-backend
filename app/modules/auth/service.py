from fastapi import HTTPException, status
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, get_password_hash, verify_password, create_access_token
from app.modules.auth.schemas import UserRegister, UserLogin
from app.modules.users import repository as user_repository
from app.modules.auth.blacklist import add



def register_user(db: Session, user_in: UserRegister):

    # check if email already exists
    existing_user = user_repository.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Este e-mail já está em uso."
        )
    
    # hashing password
    user_data = user_in.model_dump()
    password_plana = user_data.pop("password")
    user_data["password_hash"] = get_password_hash(password_plana)
    
    # creating user
    new_user = user_repository.create_user(db, user_data)
    return new_user



def authenticate_user(db: Session, user_in: UserLogin):
    # search for user by email
    user = user_repository.get_user_by_email(db, user_in.email)
    
    # verify password and user existence
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # create JWT token
    access_token = create_access_token(subject=str(user.id))
    
    return {"access_token": access_token, "token_type": "bearer"}



# Logout function that adds the token's jti to the blacklist
def logout_user(token: str):
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    jti = payload.get("jti")
    exp = payload.get("exp")

    if not jti or not exp:
        raise HTTPException(status_code=401, detail="Token inválido")

    now = datetime.now(timezone.utc)
    expire_time = datetime.fromtimestamp(exp, tz=timezone.utc)
    expires_in = int((expire_time - now).total_seconds())

    if expires_in > 0:
        add(jti, expires_in)

    return {"message": "Logout realizado com sucesso"}
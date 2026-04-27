import uuid
from fastapi import HTTPException, status
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.security import create_refresh_token, decode_token, get_password_hash, verify_password, create_access_token
from app.modules.auth.schemas import UserRegister, UserLogin
from app.modules.users import repository as user_repository
from app.modules.auth.blacklist import add



# Helper function to invalidate tokens by adding their jti to the blacklist
def _invalidate_payload(payload: dict | None):
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
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



def refresh_token(db: Session, refresh_token: str):
    payload = decode_token(refresh_token)
    
    # verify token validity
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Refresh token inválido ou expirado"
        )

    # verify token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Tipo de token inválido"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token sem identificação de usuário"
        )

    # verify if user still exists
    user = user_repository.get_user_by_id(db, user_id=uuid.UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Usuário não encontrado"
        )

    _invalidate_payload(payload)

    # generate new tokens
    new_access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))

    return {
        "access_token": new_access_token, 
        "refresh_token": new_refresh_token, 
        "token_type": "bearer"
    }



# Logout function that adds the token's jti to the blacklist
def logout_user(access_token: str, refresh_token: str | None = None):
    _invalidate_payload(decode_token(access_token))
    
    if refresh_token:
        _invalidate_payload(decode_token(refresh_token))

    return {"message": "Logout realizado com sucesso"}
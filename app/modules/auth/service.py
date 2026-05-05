import uuid
import requests
from fastapi import HTTPException, status
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.security import invalidate_payload, create_password_token, create_refresh_token, create_verification_token, decode_token, get_password_hash, verify_password, create_access_token
from app.modules.auth.schemas import GoogleRegisterRequest, UserRegister, UserLogin, UserResetPassword
from app.modules.users import repository as user_repository
from app.workers.tasks.auth import send_verification_email, send_password_email



def register_user(db: Session, user_in: UserRegister):

    # check if email already exists
    existing_user = user_repository.get_user_by_email(db, user_in.email)
    if existing_user:
        if existing_user.auth_provider == "GOOGLE":
            raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Este e-mail já está cadastrado usando o Google. Por favor, vá para a tela de acesso e clique no botão do Google.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Este e-mail já está em uso."
        )
    
    # hashing password
    user_data = user_in.model_dump()
    password_plana = user_data.pop("password")
    user_data["password_hash"] = get_password_hash(password_plana)
    user_data["auth_provider"] = "LOCAL"
    user_data["is_verified"] = False
    
    # creating user
    new_user = user_repository.create_user(db, user_data)

    # verify email
    token = create_verification_token(email=new_user.email)
    send_verification_email.delay(new_user.email, new_user.name, token)

    return new_user



def authenticate_user(db: Session, user_in: UserLogin):
    # search for user by email
    user = user_repository.get_user_by_email(db, user_in.email)

    # verify user existence first to avoid NoneType access
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.auth_provider == "GOOGLE":
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Por favor, utilize o botão 'Continuar com o Google' para entrar.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # verify password
    if not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail não verificado. Por favor, verifique seu e-mail antes de fazer login.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # create JWT token
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



def handle_google_login(db: Session, access_token: str):
    try:
        google_response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if google_response.status_code != 200:
            raise ValueError("Token do Google recusado pela API.")

        user_info = google_response.json()
        email = user_info.get("email")
        name = user_info.get("name")
        profile_picture_url = user_info.get("picture")
        
        if not email:
            raise ValueError("O token não forneceu acesso ao e-mail.")

    except Exception as e:
        print(f"[Erro Google Login] {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Token do Google inválido ou expirado."
        )

    # 2. search for user
    user = user_repository.get_user_by_email(db, email)

    if user:
        # if the user is already registered
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        
        return {
            "needs_registration": False,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    else:
        # new user
        return {
            "needs_registration": True,
            "email": email,
            "name": name,
            "profile_picture_url": profile_picture_url
        }



def register_google_user(db: Session, user_in: GoogleRegisterRequest):
    # verify if user exists
    existing_user = user_repository.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Este e-mail já está em uso."
        )
    
    user_data = user_in.model_dump()
    
    random_password = str(uuid.uuid4())
    user_data["password_hash"] = get_password_hash(random_password)
    
    user_data["is_verified"] = True 
    
    user_data["auth_provider"] = "GOOGLE"
    
    new_user = user_repository.create_user(db, user_data)

    access_token = create_access_token(subject=str(new_user.id))
    refresh_token = create_refresh_token(subject=str(new_user.id))

    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }



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

    invalidate_payload(payload)

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
    invalidate_payload(decode_token(access_token))
    
    if refresh_token:
        invalidate_payload(decode_token(refresh_token))

    return {"message": "Logout realizado com sucesso"}



def verify_user_email(db: Session, token: str):
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Token de verificação inválido ou expirado."
        )

    if payload.get("type") != "verification":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Tipo de token inválido."
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Token sem identificação de usuário."
        )

    user = user_repository.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado."
        )

    if user.is_verified:
        return {"message": "Sua conta já está verificada! Você já pode fazer login."}

    # verify user and commit to database
    user.is_verified = True
    db.commit()

    invalidate_payload(payload)

    return {"message": "E-mail verificado com sucesso!"}



def resend_email_verification(db: Session, user_email: str):
    
    generic_response = {"message": "Se o e-mail estiver cadastrado e pendente, um novo link de verificação será enviado."}

    existing_user = user_repository.get_user_by_email(db, user_email)
    
    if not existing_user or existing_user.is_verified:
        return generic_response

    user_name = existing_user.name
    token = create_verification_token(email=user_email)
    send_verification_email.delay(user_email, user_name, token)

    return generic_response



def reset_password(db: Session, user_reset_password: UserResetPassword):
    payload = decode_token(user_reset_password.token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Token de recuperação inválido ou expirado."
        )

    if payload.get("type") != "password":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Tipo de token inválido."
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Token sem identificação de usuário."
        )

    user = user_repository.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado."
        )
    
    if user.auth_provider == "GOOGLE":
        user.auth_provider = "BOTH"

    # generate new password hash and commit to database
    user.password_hash = get_password_hash(user_reset_password.new_password)
    db.commit()

    invalidate_payload(payload)

    return {"message": "Senha alterada com sucesso!"}



def send_reset_password_email(db: Session, user_email: str):
    
    generic_response = {"message": "Se o e-mail estiver cadastrado, um link para recuperação será enviado."}

    existing_user = user_repository.get_user_by_email(db, user_email)
    
    if not existing_user:
        return generic_response

    user_name = existing_user.name
    token = create_password_token(email=user_email)
    send_password_email.delay(user_email, user_name, token)

    return generic_response
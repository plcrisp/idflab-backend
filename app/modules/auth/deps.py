import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.modules.users import repository as user_repository

# warns swagger that these endpoints require authentication
security = HTTPBearer()

# dependency to get the current user from the token
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Intercepta a requisição, valida o token e devolve o usuário logado.
    """
    token = credentials.credentials
    
    # decode token to get user ID
    user_id_str = decode_access_token(token)
    
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token inválido ou expirado. Faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # search for user in database
    user = user_repository.get_user_by_id(db, user_id=uuid.UUID(user_id_str))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="O usuário dono deste token não existe mais."
        )

    return user
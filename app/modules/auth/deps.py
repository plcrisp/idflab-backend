from datetime import datetime, timezone
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.modules.users import repository as user_repository
from app.modules.auth.blacklist import exists

# warns swagger that these endpoints require authentication
security = HTTPBearer()

# dependency to get the current user from the token
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:

    token = credentials.credentials

    # decode token to get user ID
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado",
        )

    jti = payload.get("jti")

    # 🔥 CHECK BLACKLIST
    if exists(jti):
        raise HTTPException(
            status_code=401,
            detail="Token revogado",
        )

    user_id_str = payload.get("sub")

    # search for user in database
    user = user_repository.get_user_by_id(db, user_id=uuid.UUID(user_id_str))

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não existe",
        )

    return user
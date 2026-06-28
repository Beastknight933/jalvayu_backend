import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import verify_token
from app.db.session import get_db_session
from app.models.user import User, UserRole
from app.repositories.user import user_repo

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"api/v1/auth/login"
)

# Type alias for Dependency Injection
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

async def get_current_user(
    db: SessionDep, token: TokenDep
) -> User:
    """
    Validate the token and return the current user.
    """
    try:
        payload = verify_token(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise UnauthorizedException("Could not validate credentials")
            
        token_type = payload.get("type")
        if token_type != "access":
            raise UnauthorizedException("Invalid token type")
            
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise UnauthorizedException("Could not validate credentials")
        
    user = await user_repo.get(db, id=user_id)
    if not user:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise UnauthorizedException("Inactive user")
        
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

def get_current_active_superuser(current_user: CurrentUser) -> User:
    """
    Ensure the current user is an active superuser or admin.
    """
    if not current_user.is_superuser and current_user.role != UserRole.ADMIN:
        raise UnauthorizedException("The user doesn't have enough privileges")
    return current_user

class RequireRole:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles
        
    def __call__(self, current_user: CurrentUser) -> User:
        if current_user.is_superuser:
            return current_user
        if current_user.role not in self.allowed_roles:
            raise UnauthorizedException("The user doesn't have enough privileges")
        return current_user

from typing import Optional

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.exceptions import UnauthorizedException, ConflictException, NotFoundException
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.repositories.user import user_repo
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse


class AuthService:
    """
    Business logic for authentication.
    """

    async def register_user(self, db: AsyncSession, user_in: UserCreate) -> UserResponse:
        """
        Register a new user.
        """
        if user_in.password != user_in.password_confirm:
            raise ConflictException("Passwords do not match")
            
        user = await user_repo.get_by_email(db, email=user_in.email)
        if user:
            logger.warning(f"Registration failed: User with email {user_in.email} already exists")
            raise ConflictException("A user with this email already exists.")
            
        new_user = await user_repo.create(db, obj_in=user_in)
        logger.info(f"User {new_user.email} registered successfully.")
        return UserResponse.model_validate(new_user)

    async def authenticate_user(self, db: AsyncSession, form_data: OAuth2PasswordRequestForm) -> Token:
        """
        Authenticate a user and return access and refresh tokens.
        """
        user = await user_repo.get_by_email(db, email=form_data.username)
        if not user:
            raise UnauthorizedException("Incorrect email or password")
            
        if not verify_password(form_data.password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password")
            
        if not user.is_active:
            raise UnauthorizedException("Inactive user")

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        logger.info(f"User {user.email} logged in.")
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
auth_service = AuthService()

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import SessionDep, CurrentUser
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import auth_service

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    db: SessionDep,
    user_in: UserCreate,
) -> Any:
    """
    Register a new user.
    """
    return await auth_service.register_user(db, user_in=user_in)


@router.post("/login", response_model=Token)
async def login(
    db: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    return await auth_service.authenticate_user(db, form_data=form_data)


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: CurrentUser,
) -> Any:
    """
    Get current logged in user.
    """
    return current_user

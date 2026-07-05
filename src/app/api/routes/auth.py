"""Auth endpoint: prijava preko DummyJSON-a i izdavanje našeg JWT-a."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token
from app.schemas.auth import TokenResponse
from app.services import dummyjson

router = APIRouter(tags=["auth"])

logger = logging.getLogger(__name__)


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenResponse:
    user = await dummyjson.authenticate(form.username, form.password)
    if user is None:
        logger.warning("Neuspješna prijava za korisnika: %s", form.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info("Uspješna prijava: %s", form.username)
    token = create_access_token(form.username)
    return TokenResponse(access_token=token)

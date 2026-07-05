"""JWT: kreiranje i validacija access tokena.

Token je potpisan (ne šifriran) našim tajnim ključem - nitko ga ne može
krivotvoriti bez ključa. Nosi 'sub' (username) i 'exp' (istek).
"""

from datetime import UTC, datetime, timedelta

import jwt

from app.config import settings


def create_access_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """Vraća 'sub' (username) ako je token valjan i nije istekao, inače None."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.PyJWTError:
        return None
    return payload.get("sub")

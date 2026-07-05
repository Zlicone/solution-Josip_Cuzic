"""Asinkroni klijent prema vanjskom izvoru (DummyJSON).

Samo dohvat i vraćanje sirovih dictova - transformacija je u app.mappers.
"""

from typing import Any

import httpx

from app.config import settings


async def _fetch_all(
    path: str,
    key: str,
    params: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Dohvaća sve zapise s jednog DummyJSON endpointa.

    DummyJSON po defaultu vraća samo 30 zapisa; `limit=0` vraća sve odjednom,
    pa nema ručne paginacije i nijedan userId ne ostane bez usera.
    """
    query: dict[str, Any] = {"limit": 0}
    if params:
        query.update(params)

    async with httpx.AsyncClient(
        base_url=settings.dummyjson_base_url,
        timeout=settings.http_timeout,
    ) as client:
        response = await client.get(path, params=query)
        response.raise_for_status()
        return response.json()[key]


async def fetch_todos() -> list[dict[str, Any]]:
    """Svi todosi (postaju ticketi)."""
    return await _fetch_all("/todos", "todos")


async def fetch_users() -> list[dict[str, Any]]:
    """Svi useri, samo username (id uvijek dolazi) - manji payload."""
    return await _fetch_all("/users", "users", params={"select": "username"})


async def authenticate(username: str, password: str) -> dict[str, Any] | None:
    """Provjeri kredencijale preko DummyJSON /auth/login.

    Vraća korisnički objekt ako je prijava uspješna, inače None.
    """
    async with httpx.AsyncClient(
        base_url=settings.dummyjson_base_url,
        timeout=settings.http_timeout,
    ) as client:
        response = await client.post(
            "/auth/login", json={"username": username, "password": password}
        )
        if response.status_code != 200:
            return None
        return response.json()

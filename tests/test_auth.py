"""Testovi za JWT auth: prijava i zaštita write endpointa."""

import httpx
import respx

from app.config import settings
from app.core.security import create_access_token


@respx.mock
async def test_login_success_returns_token(unauth_client):
    respx.post(f"{settings.dummyjson_base_url}/auth/login").mock(
        return_value=httpx.Response(200, json={"id": 1, "username": "emilys"})
    )
    r = await unauth_client.post(
        "/auth/login", data={"username": "emilys", "password": "emilyspass"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


@respx.mock
async def test_login_invalid_credentials(unauth_client):
    respx.post(f"{settings.dummyjson_base_url}/auth/login").mock(
        return_value=httpx.Response(400, json={"message": "Invalid"})
    )
    r = await unauth_client.post(
        "/auth/login", data={"username": "x", "password": "y"}
    )
    assert r.status_code == 401


async def test_post_requires_auth(unauth_client):
    r = await unauth_client.post("/tickets", json={"title": "X"})
    assert r.status_code == 401


async def test_patch_requires_auth(unauth_client, sample_tickets):
    r = await unauth_client.patch("/tickets/1", json={"status": "closed"})
    assert r.status_code == 401


async def test_post_with_valid_token(unauth_client):
    token = create_access_token("emilys")
    r = await unauth_client.post(
        "/tickets",
        json={"title": "S tokenom"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201


async def test_read_endpoints_stay_public(unauth_client, sample_tickets):
    assert (await unauth_client.get("/tickets")).status_code == 200

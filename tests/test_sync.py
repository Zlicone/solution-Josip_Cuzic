"""Integracijski testovi sync servisa (mockan HTTP preko respx, prava test baza)."""

import httpx
import respx
from sqlalchemy import func, select

from app.config import settings
from app.db.models import Ticket
from app.services import sync

TODOS = [
    {"id": 1, "todo": "Fix login", "completed": False, "userId": 152},
    {"id": 2, "todo": "Write docs", "completed": True, "userId": 13},
    {"id": 3, "todo": "Deploy", "completed": False, "userId": 99999},  # nepoznat user
]
USERS = [{"id": 152, "username": "emilys"}, {"id": 13, "username": "noahh"}]


async def _count(session) -> int:
    return (await session.execute(select(func.count()).select_from(Ticket))).scalar_one()


@respx.mock
async def test_sync_seeds_and_maps_correctly(session):
    respx.get(f"{settings.dummyjson_base_url}/todos").mock(
        return_value=httpx.Response(200, json={"todos": TODOS})
    )
    respx.get(f"{settings.dummyjson_base_url}/users").mock(
        return_value=httpx.Response(200, json={"users": USERS})
    )

    processed = await sync.sync_tickets(session)
    assert processed == 3
    assert await _count(session) == 3

    t1 = await session.get(Ticket, 1)
    assert t1.assignee == "emilys"
    assert t1.status.value == "open"
    t3 = await session.get(Ticket, 3)
    assert t3.assignee is None  # nepoznat userId


@respx.mock
async def test_sync_is_idempotent_and_preserves_description(session):
    respx.get(f"{settings.dummyjson_base_url}/todos").mock(
        return_value=httpx.Response(200, json={"todos": TODOS})
    )
    respx.get(f"{settings.dummyjson_base_url}/users").mock(
        return_value=httpx.Response(200, json={"users": USERS})
    )

    await sync.sync_tickets(session)

    # korisnik postavi opis
    ticket = await session.get(Ticket, 1)
    ticket.description = "Rucni opis"
    await session.commit()

    # ponovni sync ne duplira i ne gazi opis
    await sync.sync_tickets(session)
    assert await _count(session) == 3
    assert (await session.get(Ticket, 1)).description == "Rucni opis"

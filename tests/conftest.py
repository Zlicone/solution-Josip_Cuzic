"""Zajednički pytest fixtures: izolirana async test baza, sesija i HTTP klijent.

Svaki test dobiva svježu in-memory SQLite bazu (StaticPool drži jednu konekciju
pa shema i podaci žive kroz cijeli test). HTTP klijent gađa app preko ASGI
transporta, uz override get_session dependencyja na test bazu.
"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_user
from app.db.base import Base
from app.db.models import Ticket, TicketPriority, TicketStatus
from app.db.session import get_session
from app.main import app


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def session(session_factory):
    async with session_factory() as s:
        yield s


def _make_session_override(session_factory):
    async def override_get_session():
        async with session_factory() as s:
            yield s

    return override_get_session


@pytest_asyncio.fixture
async def client(session_factory):
    """Autentificirani klijent (auth dependency preskočen) za većinu testova."""
    app.dependency_overrides[get_session] = _make_session_override(session_factory)
    app.dependency_overrides[get_current_user] = lambda: "testuser"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauth_client(session_factory):
    """Klijent bez override-a auth-a - za testiranje zaštite (401)."""
    app.dependency_overrides[get_session] = _make_session_override(session_factory)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_tickets(session):
    """Nekoliko ticketa raznih statusa/prioriteta za read i patch testove."""
    session.add_all(
        [
            Ticket(
                id=1, title="Fix login", status=TicketStatus.open,
                priority=TicketPriority.medium, assignee="emilys",
                source_payload={"id": 1, "todo": "Fix login"},
            ),
            Ticket(
                id=2, title="Write docs", status=TicketStatus.closed,
                priority=TicketPriority.high, assignee="noahh",
            ),
            Ticket(
                id=3, title="Fix logout bug", status=TicketStatus.open,
                priority=TicketPriority.low, description="X" * 150,
            ),
        ]
    )
    await session.commit()

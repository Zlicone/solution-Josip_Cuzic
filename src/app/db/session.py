"""Asinkroni pristup bazi: engine, tvornica sesija i FastAPI dependency.

- `engine`         – jedan po aplikaciji, drži bazen konekcija (živi cijelo vrijeme).
- `AsyncSessionLocal` – tvornica koja radi novu sesiju po potrebi.
- `get_session`    – dependency koji svakom requestu daje svježu sesiju i zatvara je.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

# Motor konekcije prema bazi. echo=True bi ispisivao SQL (korisno za debug).
engine = create_async_engine(settings.database_url, echo=False)

# Tvornica sesija. expire_on_commit=False je bitno kod asinkronog rada:
# bez toga bi objekti nakon commita "istekli" i pristup polju bi okinuo
# novi (lazy) upit u bazu, što u async svijetu radi probleme.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Daje jednu sesiju po requestu i sigurno je zatvara na kraju."""
    async with AsyncSessionLocal() as session:
        yield session

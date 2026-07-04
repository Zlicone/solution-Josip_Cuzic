"""Sync servis: dohvat iz izvora -> transformacija -> upsert u bazu.

Spaja klijent (app.services.dummyjson) i mappere (app.mappers) s bazom.
Idempotentan je: višestruko pokretanje ne duplira zapise (upsert po id-u).
"""

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Ticket
from app.db.session import AsyncSessionLocal
from app.mappers import build_username_index, todo_to_ticket_fields
from app.services import dummyjson

logger = logging.getLogger(__name__)


async def sync_tickets(session: AsyncSession) -> int:
    """Dohvati todos+users, transformiraj i upsertaj tickete u bazu.

    Vraća broj obrađenih ticketa. `description` se namjerno ne dira jer je
    to polje u vlasništvu našeg API-ja (POST/PATCH), pa ga re-sync ne gazi.
    """
    # Oba dohvata idu paralelno.
    todos, users = await asyncio.gather(
        dummyjson.fetch_todos(),
        dummyjson.fetch_users(),
    )
    username_index = build_username_index(users)

    count = 0
    for todo in todos:
        fields = todo_to_ticket_fields(todo, username_index)
        # Opis je naš (POST/PATCH), sync ga ne postavlja niti prepisuje.
        fields.pop("description", None)
        # merge = SELECT po PK pa INSERT ili UPDATE (idempotentan upsert).
        await session.merge(Ticket(**fields))
        count += 1

    await session.commit()
    logger.info("Sync gotov: %d ticketa obrađeno.", count)
    return count


async def run_sync() -> int:
    """Otvori sesiju i pokreni sync (za CLI / pozadinski job)."""
    async with AsyncSessionLocal() as session:
        return await sync_tickets(session)


def main() -> None:
    """CLI ulaz: `python -m app.services.sync`."""
    logging.basicConfig(level=settings.log_level)
    count = asyncio.run(run_sync())
    print(f"Seed/update gotov: {count} ticketa.")


if __name__ == "__main__":
    main()

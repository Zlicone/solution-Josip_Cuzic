"""Poslovna logika / repozitorij nad Ticket tablicom (čitanje).

Endpointi zovu ove funkcije; sav pristup bazi je ovdje, odvojen od HTTP sloja.
"""

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Ticket, TicketPriority, TicketStatus


async def _count(session: AsyncSession, stmt: Select) -> int:
    """Ukupan broj redova za dani (filtrirani) upit, prije paginacije."""
    count_stmt = select(func.count()).select_from(stmt.subquery())
    return (await session.execute(count_stmt)).scalar_one()


async def list_tickets(
    session: AsyncSession,
    *,
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Ticket], int]:
    """Paginirana lista uz opcionalno filtriranje po statusu i prioritetu."""
    stmt = select(Ticket)
    if status is not None:
        stmt = stmt.where(Ticket.status == status)
    if priority is not None:
        stmt = stmt.where(Ticket.priority == priority)

    total = await _count(session, stmt)
    stmt = stmt.order_by(Ticket.id).limit(limit).offset(offset)
    rows = (await session.execute(stmt)).scalars().all()
    return list(rows), total


async def get_ticket(session: AsyncSession, ticket_id: int) -> Ticket | None:
    """Jedan ticket po id-u (ili None ako ne postoji)."""
    return await session.get(Ticket, ticket_id)


async def search_tickets(
    session: AsyncSession,
    query: str,
    *,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Ticket], int]:
    """Pretraga po nazivu (case-insensitive substring)."""
    stmt = select(Ticket).where(Ticket.title.ilike(f"%{query}%"))
    total = await _count(session, stmt)
    stmt = stmt.order_by(Ticket.id).limit(limit).offset(offset)
    rows = (await session.execute(stmt)).scalars().all()
    return list(rows), total

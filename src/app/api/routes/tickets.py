"""Read endpointi za tickete: lista+filter, pretraga, detalji.

Koristi moderni FastAPI stil s Annotated tipovima za Query/Depends.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TicketPriority, TicketStatus
from app.db.session import get_session
from app.schemas.ticket import PaginatedTickets, TicketDetail, TicketListItem
from app.services import tickets as tickets_service

router = APIRouter(prefix="/tickets", tags=["tickets"])

# Ponovljive Annotated ovisnosti.
SessionDep = Annotated[AsyncSession, Depends(get_session)]
LimitDep = Annotated[int, Query(ge=1, le=100)]
OffsetDep = Annotated[int, Query(ge=0)]


@router.get("", response_model=PaginatedTickets)
async def list_tickets(
    session: SessionDep,
    status: Annotated[TicketStatus | None, Query(description="Filter po statusu")] = None,
    priority: Annotated[
        TicketPriority | None, Query(description="Filter po prioritetu")
    ] = None,
    limit: LimitDep = 20,
    offset: OffsetDep = 0,
) -> PaginatedTickets:
    rows, total = await tickets_service.list_tickets(
        session, status=status, priority=priority, limit=limit, offset=offset
    )
    return PaginatedTickets(
        items=[TicketListItem.model_validate(row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


# Mora biti PRIJE /{ticket_id}, inace FastAPI shvati "search" kao ticket_id.
@router.get("/search", response_model=PaginatedTickets)
async def search_tickets(
    session: SessionDep,
    q: Annotated[str, Query(min_length=1, description="Pojam za pretragu po nazivu")],
    limit: LimitDep = 20,
    offset: OffsetDep = 0,
) -> PaginatedTickets:
    rows, total = await tickets_service.search_tickets(
        session, q, limit=limit, offset=offset
    )
    return PaginatedTickets(
        items=[TicketListItem.model_validate(row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{ticket_id}", response_model=TicketDetail)
async def get_ticket(ticket_id: int, session: SessionDep) -> TicketDetail:
    ticket = await tickets_service.get_ticket(session, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketDetail.model_validate(ticket)

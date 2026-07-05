"""Read endpointi za tickete: lista+filter, pretraga, detalji.

Koristi moderni FastAPI stil s Annotated tipovima za Query/Depends.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.db.models import TicketPriority, TicketStatus
from app.db.session import get_session
from app.schemas.ticket import (
    PaginatedTickets,
    TicketCreate,
    TicketDetail,
    TicketListItem,
    TicketPatch,
)
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


@router.post("", response_model=TicketDetail, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    payload: TicketCreate, session: SessionDep, _user: CurrentUser
) -> TicketDetail:
    ticket = await tickets_service.create_ticket(session, payload.model_dump())
    return TicketDetail.model_validate(ticket)


@router.patch("/{ticket_id}", response_model=TicketDetail)
async def patch_ticket(
    ticket_id: int,
    payload: TicketPatch,
    session: SessionDep,
    _user: CurrentUser,
) -> TicketDetail:
    # exclude_unset -> u obzir dolaze samo polja koja je klijent stvarno poslao.
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No fields to update")
    ticket = await tickets_service.update_ticket(session, ticket_id, changes)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketDetail.model_validate(ticket)

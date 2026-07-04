"""Pydantic sheme za izlaz (serializacija ticketa prema klijentu)."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models import TicketPriority, TicketStatus

DESCRIPTION_LIST_MAX = 100


class TicketListItem(BaseModel):
    """Kratki prikaz u listi: id, title, status, priority, opis <= 100 znakova."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    description: str | None = None

    @field_validator("description")
    @classmethod
    def _truncate_description(cls, value: str | None) -> str | None:
        if value is not None and len(value) > DESCRIPTION_LIST_MAX:
            return value[:DESCRIPTION_LIST_MAX]
        return value


class TicketDetail(BaseModel):
    """Puni prikaz jednog ticketa + sirovi JSON iz izvora."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    assignee: str | None
    description: str | None
    source_payload: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


class PaginatedTickets(BaseModel):
    """Omotač za paginiranu listu."""

    items: list[TicketListItem]
    total: int
    limit: int
    offset: int


class TicketCreate(BaseModel):
    """Ulaz za POST /tickets. id se ne prima - dodjeljuje ga baza."""

    title: str = Field(min_length=1, max_length=255)
    status: TicketStatus = TicketStatus.open
    priority: TicketPriority = TicketPriority.low
    assignee: str | None = Field(default=None, max_length=100)
    description: str | None = None


class TicketPatch(BaseModel):
    """Ulaz za PATCH /tickets/{id}. Sva polja opcionalna - mijenja se samo poslano.

    Zahvaljujući model_dump(exclude_unset=True) razlikujemo "nije poslano"
    (ne diraj) od "poslano kao null" (postavi na null).
    """

    title: str | None = Field(default=None, min_length=1, max_length=255)
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assignee: str | None = Field(default=None, max_length=100)
    description: str | None = None

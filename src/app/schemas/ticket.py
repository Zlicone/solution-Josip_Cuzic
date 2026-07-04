"""Pydantic sheme za izlaz (serializacija ticketa prema klijentu)."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

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

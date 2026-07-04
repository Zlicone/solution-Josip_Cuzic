"""ORM model za Ticket + enumi za status i prioritet.

Jedan red u tablici `tickets` = jedan `Ticket` objekt u Pythonu.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TicketStatus(str, enum.Enum):
    """Status ticketa: 'closed' ako je izvorni todo completed, inače 'open'."""

    open = "open"
    closed = "closed"


class TicketPriority(str, enum.Enum):
    """Prioritet izračunat iz id-a: ['low', 'medium', 'high'][id % 3]."""

    low = "low"
    medium = "medium"
    high = "high"


class Ticket(Base):
    __tablename__ = "tickets"

    # Zadržava originalni DummyJSON todo.id na seedu; novi POST dobiva max+1.
    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255))

    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, name="ticket_status"),
        default=TicketStatus.open,
        index=True,
    )
    priority: Mapped[TicketPriority] = mapped_column(
        Enum(TicketPriority, name="ticket_priority"),
        default=TicketPriority.low,
        index=True,
    )

    # Korisničko ime razriješeno preko userId; nullable jer ga POST ne mora dati.
    assignee: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # Prazan na seedu (DummyJSON todo nema opis); puni se preko POST/PATCH.
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Sirovi JSON iz izvora (todo + razriješeni user) za GET /tickets/{id}.
    source_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Ticket id={self.id} title={self.title!r} status={self.status.value}>"

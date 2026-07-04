"""Čiste transformacijske funkcije: DummyJSON todo -> polja Ticket modela.

Namjerno bez baze i bez mreže - lako se unit-testira.
"""

from typing import Any

from app.db.models import TicketPriority, TicketStatus

# id % 3 -> prioritet
_PRIORITY_BY_MODULO = (TicketPriority.low, TicketPriority.medium, TicketPriority.high)


def map_status(completed: bool) -> TicketStatus:
    """completed == True -> 'closed', inače 'open'."""
    return TicketStatus.closed if completed else TicketStatus.open


def map_priority(todo_id: int) -> TicketPriority:
    """['low', 'medium', 'high'][id % 3]."""
    return _PRIORITY_BY_MODULO[todo_id % 3]


def build_username_index(users: list[dict[str, Any]]) -> dict[int, str]:
    """Mapa userId -> username, za razrješavanje assignee-a."""
    return {user["id"]: user["username"] for user in users if "username" in user}


def todo_to_ticket_fields(
    todo: dict[str, Any],
    username_index: dict[int, str],
) -> dict[str, Any]:
    """Pretvara jedan DummyJSON todo u dict polja spreman za Ticket(**fields).

    - title      <- todo
    - status     <- completed
    - priority   <- id % 3
    - assignee   <- username preko userId (None ako user nije nađen)
    - description = None (DummyJSON todo nema opis; puni se preko POST/PATCH)
    - source_payload = sirovi todo (za GET /tickets/{id})
    """
    return {
        "id": todo["id"],
        "title": todo["todo"],
        "status": map_status(todo["completed"]),
        "priority": map_priority(todo["id"]),
        "assignee": username_index.get(todo["userId"]),
        "description": None,
        "source_payload": todo,
    }

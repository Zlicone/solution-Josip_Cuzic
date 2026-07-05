"""Jedinični testovi za čiste mapper funkcije (bez baze i mreže)."""

import pytest

from app.db.models import TicketPriority, TicketStatus
from app.mappers import (
    build_username_index,
    map_priority,
    map_status,
    todo_to_ticket_fields,
)


def test_map_status_completed_is_closed():
    assert map_status(True) is TicketStatus.closed
    assert map_status(False) is TicketStatus.open


@pytest.mark.parametrize(
    ("todo_id", "expected"),
    [
        (3, TicketPriority.low),     # 3 % 3 == 0
        (1, TicketPriority.medium),  # 1 % 3 == 1
        (2, TicketPriority.high),    # 2 % 3 == 2
        (6, TicketPriority.low),
    ],
)
def test_map_priority_by_modulo(todo_id, expected):
    assert map_priority(todo_id) is expected


def test_build_username_index():
    users = [{"id": 5, "username": "emilys"}, {"id": 9, "username": "noahh"}]
    assert build_username_index(users) == {5: "emilys", 9: "noahh"}


def test_todo_to_ticket_fields_full_mapping():
    idx = {152: "emilys"}
    todo = {"id": 1, "todo": "Do it", "completed": False, "userId": 152}
    fields = todo_to_ticket_fields(todo, idx)
    assert fields["id"] == 1
    assert fields["title"] == "Do it"
    assert fields["status"] is TicketStatus.open
    assert fields["priority"] is TicketPriority.medium
    assert fields["assignee"] == "emilys"
    assert fields["description"] is None
    assert fields["source_payload"] == todo


def test_todo_to_ticket_fields_unknown_user_gives_none():
    todo = {"id": 2, "todo": "x", "completed": True, "userId": 99999}
    assert todo_to_ticket_fields(todo, {})["assignee"] is None

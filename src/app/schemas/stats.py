"""Sheme za agregirane statistike (GET /stats)."""

from pydantic import BaseModel


class AssigneeCount(BaseModel):
    assignee: str
    count: int


class TicketStats(BaseModel):
    total: int
    by_status: dict[str, int]
    by_priority: dict[str, int]
    top_assignees: list[AssigneeCount]

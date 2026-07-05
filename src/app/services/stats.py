"""Agregirane statistike nad ticketima."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Ticket


async def get_stats(session: AsyncSession, *, top_assignees_limit: int = 5) -> dict:
    total = (
        await session.execute(select(func.count()).select_from(Ticket))
    ).scalar_one()

    status_rows = (
        await session.execute(
            select(Ticket.status, func.count()).group_by(Ticket.status)
        )
    ).all()

    priority_rows = (
        await session.execute(
            select(Ticket.priority, func.count()).group_by(Ticket.priority)
        )
    ).all()

    assignee_rows = (
        await session.execute(
            select(Ticket.assignee, func.count())
            .where(Ticket.assignee.is_not(None))
            .group_by(Ticket.assignee)
            .order_by(func.count().desc())
            .limit(top_assignees_limit)
        )
    ).all()

    return {
        "total": total,
        "by_status": {status.value: count for status, count in status_rows},
        "by_priority": {priority.value: count for priority, count in priority_rows},
        "top_assignees": [
            {"assignee": assignee, "count": count} for assignee, count in assignee_rows
        ],
    }

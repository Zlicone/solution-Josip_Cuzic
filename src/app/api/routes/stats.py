"""Endpoint za agregirane statistike."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.stats import TicketStats
from app.services import stats as stats_service

router = APIRouter(tags=["stats"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/stats", response_model=TicketStats)
async def get_stats(session: SessionDep) -> TicketStats:
    data = await stats_service.get_stats(session)
    return TicketStats.model_validate(data)

"""Endpoint za agregirane statistike (s TTL cacheom)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache
from app.db.session import get_session
from app.schemas.stats import TicketStats
from app.services import stats as stats_service

router = APIRouter(tags=["stats"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]

_STATS_CACHE_KEY = "stats"


@router.get("/stats", response_model=TicketStats)
async def get_stats(session: SessionDep) -> TicketStats:
    cached = cache.get(_STATS_CACHE_KEY)
    if cached is not None:
        return cached
    data = await stats_service.get_stats(session)
    result = TicketStats.model_validate(data)
    cache.set(_STATS_CACHE_KEY, result)
    return result

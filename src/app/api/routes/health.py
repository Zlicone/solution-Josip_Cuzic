"""Health-check endpoint za Docker/k8s. Provjerava i dostupnost baze."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

router = APIRouter(tags=["meta"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/health")
async def health(session: SessionDep) -> dict[str, str]:
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:  # baza nedostupna
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ok"}

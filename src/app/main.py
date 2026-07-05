"""Ulazna točka aplikacije — FastAPI app factory.

Endpointi (tickets, stats, auth, health) montiraju se kroz sljedeće commite.
Za sada app factory vraća minimalnu, ali pokretljivu aplikaciju.
"""

from fastapi import FastAPI

from app.api.routes import health, stats, tickets
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Middleware REST servis koji dohvaća, pohranjuje i izlaže support tickete "
            "iz vanjskog izvora (DummyJSON) u vlastitu bazu."
        ),
    )

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        return {"service": settings.app_name, "version": settings.app_version}

    app.include_router(tickets.router)
    app.include_router(stats.router)
    app.include_router(health.router)

    return app


app = create_app()

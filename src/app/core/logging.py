"""Konfiguracija logiranja (razina iz postavki: INFO/WARNING/ERROR...)."""

import logging

from app.config import settings


def configure_logging() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)-8s %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

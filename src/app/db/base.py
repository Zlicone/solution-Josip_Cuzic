"""Deklarativna baza za sve ORM modele.

Svi modeli nasljeđuju `Base`. Preko `Base.metadata` SQLAlchemy (i Alembic)
znaju popis svih tablica u shemi.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

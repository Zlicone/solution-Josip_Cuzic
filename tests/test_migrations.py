"""Dokaz da Alembic migracije čisto kreiraju shemu na praznoj bazi.

Pokreće `alembic upgrade head` u zasebnom procesu s privremenom bazom, pa
provjerava da tablica 'tickets' postoji.
"""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_migrations_create_tickets_table(tmp_path):
    db_path = tmp_path / "migration_test.db"
    env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{db_path}"}

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    con = sqlite3.connect(db_path)
    try:
        tables = {
            row[0]
            for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    finally:
        con.close()
    assert "tickets" in tables

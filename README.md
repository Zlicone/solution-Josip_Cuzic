# TicketHub

Middleware REST servis koji dohvaća "support tickete" iz vanjskog izvora (DummyJSON),
transformira ih u vlastiti model, pohranjuje u lokalnu bazu i izlaže preko FastAPI-ja.
Svi read/write endpointi rade nad **lokalnom bazom**, nikad nad živim pozivom prema izvoru.

> 🚧 Work in progress — gradi se feature po feature (vidi commit povijest).

## Tehnološki stack

- **Python 3.11** — typing, async/await
- **FastAPI 0.111** — automatski OpenAPI opis
- **SQLAlchemy 2.x** (async) + **aiosqlite** — pristup bazi
- **Alembic** — migracije sheme
- **pydantic 2.7** / **pydantic-settings** — validacija i konfiguracija
- **httpx 0.27** — pozivi prema vanjskom izvoru
- **pytest** — jedinični i integracijski testovi

## Brzi početak

```bash
# 1. Virtualno okruženje
python3.11 -m venv .venv
source .venv/bin/activate

# 2. Instalacija (uklj. dev alate)
pip install -e ".[dev]"

# 3. Konfiguracija
cp .env.example .env      # po potrebi uredi vrijednosti

# 4. Pokretanje
uvicorn app.main:app --reload
```

Nakon pokretanja: OpenAPI docs na `http://127.0.0.1:8000/docs`.

## Konfiguracija (env varijable)

Sve postavke imaju razumne defaulte (vidi `src/app/config.py`); nadjačavaju se preko `.env`.
Najvažnije:

| Varijabla            | Default                                   | Opis                    |
|----------------------|-------------------------------------------|-------------------------|
| `DATABASE_URL`       | `sqlite+aiosqlite:///./tickethub.db`      | Async konekcija na bazu |
| `DUMMYJSON_BASE_URL` | `https://dummyjson.com`                   | Vanjski izvor podataka  |
| `SEED_ON_STARTUP`    | `false`                                   | Seed baze na startupu   |

## Struktura projekta

```
src/app/        # aplikacijski kod (config, main, db, schemas, services, api, core)
tests/          # jedinični i integracijski testovi
alembic/        # migracije sheme baze
.github/workflows/  # CI (GitHub Actions)
```

## Korištenje AI alata

Dokumentirano u završnoj verziji README-a (gdje i zašto je korišten AI alat, uz priložen prompt).

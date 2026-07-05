# TicketHub

Middleware REST servis koji dohvaća „support tickete" iz vanjskog izvora (DummyJSON),
transformira ih u vlastiti model, pohranjuje u lokalnu bazu i izlaže preko FastAPI-ja.
Svi read i write endpointi rade nad **lokalnom bazom**, nikad nad živim pozivom prema izvoru.

![CI](https://github.com/Zlicone/solution-Josip_Cuzic/actions/workflows/ci.yml/badge.svg)

## Tehnološki stack

- **Python 3.11** — typing, async/await
- **FastAPI 0.111** — automatski OpenAPI opis
- **SQLAlchemy 2.x** (async) + **aiosqlite** — asinkroni pristup bazi
- **Alembic** — migracije sheme
- **pydantic 2.7** / **pydantic-settings** — validacija i konfiguracija
- **httpx 0.27** — pozivi prema vanjskom izvoru
- **PyJWT** — autentifikacija
- **pytest** + **respx** — jedinični i integracijski testovi
- **ruff** — lint i formatiranje

## Brzi početak

```bash
# 1. Virtualno okruženje
python3.11 -m venv .venv
source .venv/bin/activate          # Windows (Git Bash): source .venv/Scripts/activate

# 2. Instalacija (uklj. dev alate)
pip install -e ".[dev]"

# 3. Konfiguracija (opcionalno - postoje razumni defaulti)
cp .env.example .env

# 4. Migracije baze
alembic upgrade head

# 5. Napuni bazu iz vanjskog izvora (seed)
python -m app.services.sync

# 6. Pokretanje
uvicorn app.main:app --reload
```

Nakon pokretanja: interaktivni OpenAPI docs na `http://127.0.0.1:8000/docs`.

## Konfiguracija (env varijable)

Sve postavke imaju razumne defaulte (vidi `src/app/config.py`); nadjačavaju se preko `.env`.

| Varijabla            | Default                                   | Opis                       |
|----------------------|-------------------------------------------|----------------------------|
| `DATABASE_URL`       | `sqlite+aiosqlite:///./tickethub.db`      | Async konekcija na bazu    |
| `DUMMYJSON_BASE_URL` | `https://dummyjson.com`                   | Vanjski izvor podataka     |
| `SEED_ON_STARTUP`    | `false`                                   | Seed baze na startupu      |
| `JWT_SECRET`         | `change-me-in-production`                 | Tajni ključ za JWT         |
| `JWT_EXPIRE_MINUTES` | `60`                                      | Trajanje access tokena     |
| `CACHE_TTL_SECONDS`  | `60`                                      | TTL za in-memory cache     |
| `LOG_LEVEL`          | `INFO`                                    | Razina logiranja           |

## Endpointi

**Read (javni)**

| Metoda | Putanja                            | Opis                                    |
|--------|------------------------------------|-----------------------------------------|
| GET    | `/tickets`                         | Paginirana lista (+ filter `status`, `priority`) |
| GET    | `/tickets/search?q=`               | Pretraga po nazivu                      |
| GET    | `/tickets/{id}`                    | Detalji + puni JSON iz izvora           |
| GET    | `/stats`                           | Agregirane statistike (cachirano)       |
| GET    | `/health`                          | Health-check (provjerava i bazu)        |

**Write (traže JWT)**

| Metoda | Putanja            | Opis                        |
|--------|--------------------|-----------------------------|
| POST   | `/auth/login`      | Prijava preko DummyJSON-a → JWT |
| POST   | `/tickets`         | Kreiranje ticketa           |
| PATCH  | `/tickets/{id}`    | Izmjena ticketa             |

### Autentifikacija

Write endpointi traže `Authorization: Bearer <token>`. Token se dobiva prijavom
preko DummyJSON kredencijala (npr. `emilys` / `emilyspass`):

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=emilys&password=emilyspass"
```

U `/docs` se koristi dugme **Authorize**.

## Testovi

```bash
pytest
```

Pokriva: mappere (unit), sync servis (integracija, mockan HTTP preko respx),
sve read/write endpointe, auth, caching, i primjenu Alembic migracija.

## Struktura projekta

```
src/app/
├── main.py              # app factory, montiranje routera
├── config.py            # postavke (pydantic-settings)
├── mappers.py           # DummyJSON -> Ticket (čiste funkcije)
├── db/                  # Base, async session, ORM modeli
├── schemas/             # pydantic sheme (ulaz/izlaz)
├── services/            # dummyjson klijent, sync, tickets, stats
├── core/                # security (JWT), cache, logging
└── api/                 # deps + routes (tickets, stats, health, auth)
alembic/                 # migracije sheme baze
tests/                   # jedinični i integracijski testovi
.github/workflows/       # CI (GitHub Actions)
```

## Transformacija podataka

Vanjski todo → vlastiti Ticket:

- `id` — iz `todo.id`
- `title` — iz `todo.todo`
- `status` — `closed` ako `completed == true`, inače `open`
- `priority` — `["low", "medium", "high"][id % 3]`
- `assignee` — `username` razriješen preko `userId`

## Odluke i pretpostavke

- **Baza:** SQLite + aiosqlite (async, bez infrastrukture). `DATABASE_URL` je env varijabla
  pa je prebacivanje na PostgreSQL trivijalno.
- **`description`:** DummyJSON todo nema opis, pa je to zaseban nullable stupac — prazan na
  seedu, puni se preko POST/PATCH. U listi se prikazuje skraćen na 100 znakova. Sync ga
  namjerno ne dira da ne pregazi korisničke izmjene.
- **`source_payload`:** sirovi JSON iz izvora čuva se u JSON stupcu za `GET /tickets/{id}`.
- **Seed:** eksplicitan (`python -m app.services.sync`); upsert po id-u, pa je idempotentan.
  Svi endpointi rade nad lokalnom bazom, nikad nad živim DummyJSON pozivom.
- **`id` novih ticketa:** dodjeljuje baza (nastavlja se na seedane).
- **Auth:** štiti samo write endpointe; read je javan.
- **Cache:** in-memory TTL na `/stats`; svaki write ga čisti. Isto `get/set/clear` sučelje
  kao Redis, pa bi se lako skaliralo.
- **Users:** dohvaćaju se svi (`limit=0`) jer `userId` u todosima ide izvan defaultnih 30.

## Korištenje AI alata

Projekt je izrađen uz pomoć AI asistenta (Claude) kao pair-programming partnera: planiranje
arhitekture, generiranje i objašnjavanje koda te postavljanje testova, korak po korak uz
provjeru svakog dijela. Sav kod je pregledan i pokrenut lokalno.

Primjer prompta korištenog tijekom izrade:

> „Gradimo TicketHub — FastAPI middleware s async SQLAlchemy 2.x, Alembic migracijama i
> pytest testovima. Idemo feature po feature, jedan commit po featureu. Objasni mi async
> SQLAlchemy pattern (engine, session, get_session dependency) prije nego napišemo db sloj."

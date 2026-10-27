# Zayn Resort

A hotel reservation REST API built with Python. A study and portfolio project focused on layered architecture, data integrity and testing.

## Stack

Python 3.14 · FastAPI · Pydantic v2 · PostgreSQL 18 · psycopg v3 (raw SQL, no ORM) · Alembic · pytest

## Features

**Reservations (core of the system)**
- Creation with date validation, customer/room/category checks, date-range conflict detection and automatic `total_amount` calculation (daily rate × number of days).
- Date changes (`PATCH /reservations/{id}/dates`) with a new conflict check and total recalculation. Not allowed for `cancelled` or `checked_out` reservations.
- Status changes (`PATCH /reservations/{id}/status`) driven by a state machine.
- Only `confirmed` and `checked_in` reservations count as room occupancy.

**Catalog and customers**
- Room categories (name, capacity, daily rate) and rooms linked to a category.
- Customers with an 11-digit CPF, date of birth and newsletter opt-in.

**All entities**
- Full CRUD (POST, GET, PUT, PATCH, DELETE) with soft delete (`deleted_at`) and timestamps.
- Input normalization (leading/trailing whitespace is stripped) and rejection of unknown fields (`extra="forbid"`).
- Case-insensitive uniqueness (category name, room number) that works together with soft delete.
- A category with active rooms, or a room or customer with active reservations (`confirmed` or `checked_in`), cannot be deleted (409).

### Reservation state machine

```
confirmed ──► checked_in ──► checked_out
    │
    └──────► cancelled
```

`checked_out` and `cancelled` are final states. Any other transition returns 409.

## Architecture

```
Request → Schema → Route → (Service) → Repository → Database
```

| Layer | Responsibility |
|---|---|
| Schema | Validates and normalizes input with Pydantic. Errors become 422 without touching the database. |
| Route | HTTP layer: status codes, `response_model` and translation of domain exceptions into `HTTPException`. |
| Service | Reservation only: state machine, `total_amount` and date conflicts. Knows nothing about HTTP. |
| Repository | SQL only, in the repository of the queried table. Never raises domain exceptions. |
| `database.py` | Single access point to the database (`execute_query`). |

Domain exceptions live in `app/services/reservation_exceptions.py`.

## Design decisions

**Reservations and business rules**
- **Service without HTTP:** the Service raises domain exceptions and the Route translates them into HTTP status codes.
- **Validation order:** own resource (404) → empty body (400) → related resources (404) → rule or uniqueness (409). On reservation creation: dates (422) → customer → room → category (404) → conflict (409) → calculation → INSERT.
- **UPDATE with `if not result`:** an UPDATE can affect zero rows because of a race condition, so an empty result becomes 404. `INSERT ... RETURNING` raises an exception instead of returning empty.
- **Status enum:** `ReservationStatus(str, Enum)` inherits `str` comparison but overrides `__str__`. That is why the value is converted with `.value` at the Service → Repository boundary.

**Data and database**
- **Money:** `Decimal` and `NUMERIC(10,2)`, never `float`. In JSON, `Decimal` is serialized as a string.
- **Code is UX, the database is integrity:** validations in code give good error messages, and database constraints guarantee consistency.
- **Soft delete and uniqueness:** a plain `UNIQUE` does not work with soft delete. I use partial unique indexes (`WHERE deleted_at IS NULL`) on `LOWER(col)` when the comparison is case-insensitive, and the query uses the same expression as the index.
- **FKs do not protect against soft delete:** soft delete is an `UPDATE`, so the referenced row still exists. The "in use" rule lives in the application, with read queries before the delete.
- **Explicit queries:** named columns (no `*`) and `RETURNING` to return what was persisted.

**API and schemas**
- **PUT replaces, PATCH updates partially:** PATCH uses `model_dump(exclude_unset=True)`.
- **Separate schemas:** input schemas use `extra="forbid"`, response schemas do not. Fields that are optional in the database use `| None = None` in the response.
- **Responses:** POST, PUT and PATCH return the full object, and DELETE returns 204 with no body.
- **DELETE:** 404 if the resource never existed and 409 if it was already deleted.

**Migrations**
- Alembic, with small, reversible migrations (`downgrade` is the inverse, in reverse order). Applied migrations are never edited.
- Current constraints and indexes: CHECK on `reservations.status`, partial unique index on CPF (`customers_cpf_active_unique`), partial unique indexes on category name and room number (on `LOWER`) and a partial index on `reservations.room_id`.

**Configuration**
- The connection comes from `DATABASE_URL`, defined in `.env` (kept out of Git). `.env.example` documents the format.

## Getting started

**Prerequisites:** Python 3.14 and PostgreSQL 18 with a database named `zayn_resort`.

```powershell
git clone https://github.com/zaynachahin/zayn-resort.git
cd zayn-resort
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python -m uvicorn app.main:app --reload
```

Edit `.env` with your own values. It must never be committed:

```
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/zayn_resort
```

Special characters in the password must be URL-encoded (`@` becomes `%40`, `%` becomes `%25`).

Interactive documentation: `http://localhost:8000/docs`

## Endpoints

| Resource | Routes |
|---|---|
| Customers | `GET/POST /customers`, `GET/PUT/PATCH/DELETE /customers/{customer_id}` |
| Room categories | `GET/POST /room-categories`, `GET/PUT/PATCH/DELETE /room-categories/{id}` |
| Rooms | `GET/POST /rooms`, `GET/PUT/PATCH/DELETE /rooms/{id}` |
| Reservations | `GET/POST /reservations`, `GET/DELETE /reservations/{id}`, `PATCH /reservations/{id}/dates`, `PATCH /reservations/{id}/status` |

### Status codes

| Code | Usage |
|---|---|
| 201 | Resource created |
| 204 | Successful delete, no body |
| 400 | Valid request that makes no sense (empty PATCH) |
| 404 | Resource does not exist |
| 409 | State conflict (duplicate, already deleted, in use, period unavailable, invalid transition) |
| 422 | Invalid request, rejected before touching the database |

## Tests

```powershell
python -m pytest -v
```

The suite follows the AAA pattern (Arrange, Act, Assert) and DRY, using `monkeypatch` where the function is used. Since repositories are mocked, **the tests do not execute SQL**. Queries, constraints and indexes were validated manually in `psql` and through the API.

The suite has 125 tests.

## Project structure

```
app/
  main.py
  database.py
  repositories/    # SQL, one file per table
  routes/          # HTTP layer
  schemas/         # input and response (Pydantic)
  services/        # Reservation rules and domain exceptions
alembic/versions/  # migrations (source of truth for the schema)
tests/             # tests and conftest.py (client fixture)
schema.sql         # initial schema (historical; may be outdated)
seed.sql           # sample data
pytest.ini
.env.example
alembic.ini.example
```

## Known limitations

- **One connection per query:** no pool and no per-request transaction. Checking and writing happen in separate transactions, so there is a race condition risk (for example, two simultaneous reservations for the same period, or a concurrent delete with a usage check).
- No integration tests against a real PostgreSQL.
- No authentication or authorization.
- 409 error messages are not yet standardized across entities.
- GET endpoints return hand-built dicts, without `response_model`.

## Roadmap

- Connection pool and one transaction per request (with `SELECT ... FOR UPDATE`).
- Exclusion constraint to prevent overlapping reservations in the database.
- Integration tests against a real PostgreSQL.
- Authentication.
- `response_model` on GET endpoints and protection against `KeyError` in status transitions.
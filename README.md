# Personal OS

A production-grade, single-user personal operating system replacing Notion, YNAB, Readwise, and spreadsheet sprawl. Built for power users and AI agents alike.

This setup is configured to run **entirely locally** for testing with no external cloud dependencies.

---

## Architecture

```
personal-os/
├── apps/
│   ├── api/          # FastAPI backend (Python 3.12)
│   └── web/          # Next.js 15 frontend (TypeScript)
├── packages/
│   └── shared-types/ # Shared TypeScript type definitions
├── docker-compose.yml
└── turbo.json
```

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 15, shadcn/ui, Tailwind CSS, TanStack Query, Zustand, cmdk |
| Backend | FastAPI, SQLAlchemy 2.0 (async), Alembic, Celery |
| Database | PostgreSQL 16 + pgvector |
| Cache & Queue | Redis 7 |
| Auth | JWT (argon2) |

---

## Local Setup & Quick Start

### Prerequisites

Ensure you have the following installed on your machine:
- **Node.js 20+**
- **Python 3.12+**
- **Docker Desktop**

---

### Step 1: Clone and Install Node Workspace
In your terminal, run:
```bash
npm install
```

---

### Step 2: Set Up Environment Variables
Copy the templates to their active local files:

**Root Env (for Docker Compose)**:
```bash
cp .env.example .env
```

**Backend Env**:
```bash
cp apps/api/.env.example apps/api/.env
```

**Frontend Env**:
```bash
cp apps/web/.env.example apps/web/.env.local
```

---

### Step 3: Spin Up Local Postgres & Redis
Start the database and cache layers inside Docker:
```bash
docker compose up -d
```
*Note: This configuration uses named volumes (`pgdata` and `redisdata`) to persist your data locally across restarts. Use `docker compose down -v` if you wish to wipe the database clean.*

---

### Step 4: Python Backend Setup & Seeding
Create a python virtual environment, install dependencies, run database migrations, and seed default test data:

```bash
# Navigate to the API application
cd apps/api

# Create & activate venv
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install all backend packages in editable/development mode
pip install -e ".[dev]"

# Run database migrations using Alembic
alembic upgrade head

# Seed initial test data (test@example.com / password123, accounts, transactions, books)
python seed.py
```

---

### Step 5: Running the Applications (Local Development)

To run the full stack locally:

#### 1. Start the API backend (FastAPI)
From the `apps/api/` directory (inside your activated `.venv`):
```bash
uvicorn app.main:app --reload --port 8000
```
- API Endpoint: `http://localhost:8000`
- Interactive Swagger documentation: `http://localhost:8000/docs`

#### 2. Start the Celery background worker
From the `apps/api/` directory (inside your activated `.venv`):
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```
- Broker: Local Redis (`redis://localhost:6379/0`)

#### 3. Start the Next.js Frontend App
From the root of the repository:
```bash
npm run dev
```
- Dashboard UI will be available at: `http://localhost:3000`
- Sign in with the seeded credentials:
  - **Email**: `test@example.com`
  - **Password**: `password123`

---

## Database Commands

Run these commands inside the `apps/api` folder under your `.venv`:

- **Run all migrations**: `alembic upgrade head`
- **Create new migration**: `alembic revision --autogenerate -m "describe changes"`
- **Reset database schema**: `alembic downgrade base && alembic upgrade head`
- **Re-seed data**: `python seed.py`

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl+K` | Toggle Command palette |
| `Cmd/Ctrl+N` | Toggle Quick capture |
| `G → D` | Go to Home dashboard |
| `G → F` | Go to Finance page |
| `G → B` | Go to Books page |
| `G → H` | Go to Habits & Journal page |
| `G → N` | Go to Notes page |
| `G → T` | Go to Tools builder page |
| `?` | Toggle Shortcut cheatsheet overlay |
| `Esc` | Close modal / cancel overlay |

---

## License

Private single-user application. All rights reserved.

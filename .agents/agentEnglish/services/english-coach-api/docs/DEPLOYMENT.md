# Production Deployment Architecture Guide

This document details staging and production container deployments for the **Warborn Multi-Agent Platform Core**.

---

## 1. Local Development (Standard)

The platform is designed to be fully self-contained and runnable locally with zero external requirements:
```bash
# Run migrations
$env:PYTHONPATH="."; .venv\Scripts\alembic upgrade head

# Run server
.venv\Scripts\uvicorn app.main:app --reload
```
By default, `CELERY_ENABLED` and `AUTH_ENABLED` are set to `False` to prevent developer setup blockages.

---

## 2. Docker Compose (Redis Broker Stack)

For container-based staging and integration test runs, use Docker Compose to spawn a Redis instance, FastAPI app, and Celery workers:

```bash
# Copy and verify environment variables
cp .env.staging.example .env

# Build and boot container services
docker compose up --build -d
```

---

## 3. Production Deployment Checks

Before launching in production, verify:
- **Database Engine**: Swap the default SQLite backend url for a highly available Postgres connection string:
  ```env
  DATABASE_URL=postgresql+asyncpg://<user>:<password>@<db-host>:5432/<db-name>
  ```
- **Secrets Management**: Provide custom values for `JWT_SECRET_KEY` and `ADMIN_API_KEY`.
- **Startup Diagnostics**: Read logs to verify that the boot validators successfully verified database schema upgrades and Redis queue connections.

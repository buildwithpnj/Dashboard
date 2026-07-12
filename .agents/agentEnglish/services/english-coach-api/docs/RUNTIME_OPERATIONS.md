# Runtime Operations & Telemetry

This guide explains how to monitor application state and perform operational actions on the **Warborn Multi-Agent Platform Core**.

---

## 1. Health Probe Telemetry

The application exposes three diagnostic endpoints under the `/v1/coach/health` namespace for container routing and orchestrator probes:

- **Liveness Probe** (`/v1/coach/health/live`):
  Checks if the web server thread loop is operational. Always returns `{"status": "alive"}`.
- **Readiness Probe** (`/v1/coach/health/ready`):
  Checks active SQL database transaction availability by running a quick ping query (`select 1`).
- **Dependencies Diagnostics** (`/v1/coach/health/dependencies`):
  Aggregates connection statuses for the database and Redis instances, raising `503 Service Unavailable` if critical systems go offline.

---

## 2. Structured JSON Event Logs

All operations write to stdout as structured JSON objects:
```json
{"request_id": "req-123", "provider": "MockLLMProvider", "model": "unknown-model", "latency_ms": 13.8, "text_preview": "Hello..."}
```
These logs are collected by container forwarders (e.g. FluentBit) and shipped to central indexes (e.g. OpenSearch) for querying.

---

## 3. Database Schema Migrations

Database schema changes are managed via Alembic. Apply head updates during deployment pipelines:
```bash
alembic upgrade head
```
The application dynamically performs check checks on startup to confirm migration levels.

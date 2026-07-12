# Warborn Multi-Agent Platform Core - API Backend V3.5

Warborn Multi-Agent Platform Core is a private, production-grade personal agent API supporting three coach products over shared database persistence, memory retrieval, background job threads, and security/tenancy isolation walls.

---

## 1. Hardening V3.5 Additions
- **Config-Driven Security (Auth & RBAC)**: Secure routes dynamically using `AUTH_ENABLED` toggle, supporting `X-API-KEY` header authentication and Bearer JWT decoding. Enforces role checks (`admin` or `user`) on endpoints.
- **Data Scoping Walls (Multi-Tenancy)**: Database operations query models (`learner_profiles`, `sessions`, `family_profiles`, `checkin_runs`) scoped strictly under the requester's `tenant_id` context. Uses tenant-prefixed primary keys to eliminate collisions.
- **In-Memory Background Worker**: Queues long-running operations asynchronously using `BackgroundJobWorker` powered by a `ThreadPoolExecutor` context pool, executing session memory consolidation and live rating checks in separate loop contexts.
- **Richer Observability (Tracing & Metrics)**: Nested trace execution spans logging start/finish stamps, and tracking counts for auth denials, background jobs, and context budgets drops.

---

## 2. Directory Structure

```
services/english-coach-api/
├── app/
│   ├── api/
│   │   ├── deps.py               # Dependency injection container (async DB-ready)
│   │   └── v1/
│   │       └── routers/
│   │           ├── coach.py      # Secure /respond and /feedback routes
│   │           ├── lifeos.py     # Secure /lifeos/respond endpoint
│   │           ├── family.py     # Secure /family/checkin endpoint
│   │           ├── voice.py      # Secure /voice/respond endpoint
│   │           ├── health.py     # GET /health endpoint
│   │           └── admin.py      # Secure GET /admin/metrics endpoint
│   ├── core/
│   │   ├── config.py             # Pydantic Settings (active DATABASE_URL & auth variables)
│   │   └── log_config.py        # Observability structured JSON logger
│   ├── db/
│   │   ├── base.py               # Declarative ORM metadata aggregator
│   │   ├── models.py             # DB models (Configs, Sessions, Messages, Checkins)
│   │   └── session.py            # Async engine and startup table creator
│   ├── products/
│   │   ├── english_coach/        # Modular English Coach split
│   │   ├── lifeos_coach/         # Modular Health Coach split
│   │   └── family_checkin/       # Modular Wellness Check-in split
│   ├── prompts/
│   │   └── prompt_library.py     # Stable prefix prompts & token estimator
│   ├── providers/
│   │   ├── base.py               # Provider contract DTOs
│   │   ├── mock_provider.py      # Offline mock provider with product switches
│   │   └── openai_provider.py    # OpenAI completions API adapter
│   ├── repositories/
│   │   ├── base.py               # Base DB repositories templates
│   │   ├── learner_profiles.py   # Scoped learner profile database queries
│   │   ├── sessions.py           # Scoped conversation session query manager
│   │   ├── messages.py           # Message repository persistence
│   │   ├── product_configs.py    # Global product config database queries
│   │   ├── family_profiles.py    # Scoped family profiles database queries
│   │   ├── checkins.py           # Scoped wellness runs database queries
│   │   └── approved_examples.py  # Dual-mode approved corrections storage
│   ├── security/
│   │   ├── auth.py               # API key and JWT token auth validator
│   │   └── rbac.py               # Allowed roles checker dependency
│   ├── services/
│   │   ├── memory_service.py     # DB-backed dynamic memory context retrieval
│   │   ├── context_budget.py     # Token clipping context guardrail service
│   │   ├── transcription_service.py # Speech-to-text (STT) transcription stub
│   │   ├── tts_service.py        # Text-to-speech (TTS) speech synthesis stub
│   │   ├── voice_service.py      # Voice coordinator pipeline wrapper
│   │   ├── critic_service.py     # Critic scanning for prompt leaks
│   │   └── quality_gate.py       # Quality gate and repair loop controller
│   ├── tasks/
│   │   ├── worker.py             # In-memory ThreadPool background worker
│   │   └── jobs.py               # Memory consolidation & live eval jobs
│   └── main.py                 # ASGI app initialization & startup creator
├── alembic/
│   ├── env.py                    # Async migrations environment file
│   └── versions/                 # Version-controlled migration history
├── tests/
│   ├── test_health.py            # GET /health assertions
│   ├── test_coach.py             # English Coach route test
│   ├── test_repositories.py      # Assert database CRUD operations
│   ├── test_sessions.py          # Assert chat sessions and message persistence
│   ├── test_voice.py             # Assert voice transcription and synthesis stubs
│   ├── test_family_checkin.py    # Assert safety check-ins and escalations
│   ├── test_orchestration.py     # Assert intent routing heuristics
│   ├── test_quality_gate.py      # Assert critic leak warnings and repair passes
│   ├── test_admin_auth.py        # Verify API key, JWT auth token decoding, and RBAC
│   ├── test_tenancy.py          # Verify database tenancy query partition
│   └── test_jobs.py              # Verify thread execution of background worker tasks
├── scripts/
│   ├── seed_db.py                # Database setup & configuration seeder
│   ├── run_evals.py              # Driving accuracy evaluation datasets
│   └── generate_eval_report.py   # Print visual console accuracy summaries
```

---

## 3. Environment Config Keys

Configure the following variables inside your `.env` file to control the security and tenancy layer:

```env
# Auth config (disabled locally by default to prevent testing breakages)
AUTH_ENABLED=False
ADMIN_API_KEY=warborn_admin_secret
JWT_SECRET_KEY=super_jwt_secret_key
DEFAULT_TENANT_ID=default_tenant
```

---

## 4. Run Verification Suite

To run database migrations and execute the verification test matrix:

```bash
# Run database migrations
$env:PYTHONPATH="."; .venv\Scripts\alembic upgrade head

# Run all 30 tests
.venv\Scripts\pytest
```

---

## 5. Handoff to V4 (Roadmap)
- **Celery / Redis Worker Upgrade**: Transition `BackgroundJobWorker` from threads to a distributed Celery backend.
- **WebSocket Spoken Streams**: Implement real-time WebSockets to stream voice audio data.
- **Active pgvector Search**: Swap local SQLite database configurations for a cloud PostgreSQL engine to enable semantic searches.

# Job Aggregator

Scam-free job aggregation with verified sources, W2 filtering, and trust scoring.

Pulls jobs from verified sources (company career pages, Bloomberry API), filters out ghost jobs and scams, classifies W2 vs C2C, and assigns a trust score to every listing.

## Quick Start

```bash
# 1. Start PostgreSQL + Redis
make db-up

# 2. Install dependencies
make dev-deps

# 3. Run database migrations
make migrate

# 4. Start the dev server
make dev
```

The API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | Python 3.11+ / FastAPI | Async, fast, great for data processing |
| Database | PostgreSQL 16 | Reliable, JSONB for flexible flag storage |
| Cache | Redis 7 | Fast dedup checks, API response caching |
| Migrations | Alembic | Schema versioning with autogenerate |
| Frontend | React + Vite + TypeScript | Interactive filter dashboard (Phase 4) |

## Project Structure

```
job-aggregator/
├── src/job_aggregator/
│   ├── api/                # FastAPI routes and middleware
│   │   ├── app.py          # App factory with lifespan events
│   │   ├── deps.py         # Dependency injection (DB, Redis)
│   │   └── routes/         # Endpoint modules
│   ├── core/               # Configuration and shared schemas
│   │   ├── config.py       # pydantic-settings (env vars)
│   │   └── models.py       # Pydantic request/response models
│   ├── db/                 # Database layer
│   │   ├── tables.py       # SQLAlchemy ORM models
│   │   ├── engine.py       # Async engine + session factory
│   │   └── redis.py        # Redis client + dedup helpers
│   ├── sources/            # Job source adapters (Phase 2)
│   ├── filters/            # W2 classifier, scam detector (Phase 2)
│   ├── enrichment/         # Company verification (Phase 3)
│   └── scheduler/          # Background job fetching (Phase 3)
├── tests/                  # pytest test suite
├── alembic/                # Database migrations
├── docker-compose.yml      # PostgreSQL + Redis for dev
├── pyproject.toml          # Dependencies and tool config
└── Makefile                # Development commands
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check (DB + Redis status) |
| `GET` | `/api/jobs` | List jobs with filters and pagination |
| `GET` | `/api/jobs/{id}` | Get a single job by ID |

### Job Filters (`GET /api/jobs`)

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search title and description |
| `employment_type` | enum | `w2_fulltime`, `w2_contract`, `c2c`, `1099` |
| `source` | enum | `bloomberry`, `linkedin`, `indeed`, `rss`, `direct` |
| `min_trust_score` | float | 0.0 - 1.0 |
| `max_age_days` | int | Filter out jobs older than N days |
| `min_salary` | int | Minimum salary filter |
| `location` | string | Location keyword search |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Results per page (1-100, default: 25) |

## Trust Scoring

Every job gets a trust score from 0.0 (likely scam) to 1.0 (verified):

| Score | Level | Meaning |
|-------|-------|---------|
| 0.7 - 1.0 | High | Verified source, real company, fresh posting |
| 0.4 - 0.69 | Medium | Some verification, minor flags |
| 0.0 - 0.39 | Low | Multiple red flags, proceed with caution |

### Red Flags (lower score)

- Job only exists on third-party boards (not company careers page)
- Posted 30+ days ago (likely a ghost job)
- Vague description, no specific tech stack
- Contact via personal email (Gmail, Yahoo, Telegram)
- Mentions "equipment fees" or upfront costs

### Green Flags (higher score)

- Found on official company careers page
- Posted within the last 7 days
- Detailed description with specific technologies
- Contact via company domain email
- Mentions W2 benefits (401k, PTO, health insurance)

## Development

```bash
make help           # Show all available commands
make dev            # Start dev server with auto-reload
make test           # Run tests
make test-cov       # Run tests with coverage
make lint           # Check linting
make lint-fix       # Auto-fix lint issues
make typecheck      # Run mypy type checker
make db-up          # Start PostgreSQL + Redis
make db-down        # Stop services (keeps data)
make db-reset       # Stop + delete all data
make migrate        # Run pending migrations
make migrate-create MSG="description"  # Create new migration
```

## Configuration

All settings are loaded from environment variables (with `.env` file support).
See [`.env.example`](.env.example) for the full list.

## Roadmap

- [x] Phase 1: Foundation (project structure, DB models, API scaffolding)
- [ ] Phase 2: Source adapters + filter engine (Bloomberry, RSS, W2 classifier, scam detector)
- [ ] Phase 3: Enrichment pipeline (company verification, title expansion, scheduler)
- [ ] Phase 4: React frontend dashboard

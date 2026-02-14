# Design Document — Job Aggregator

## Problem

Job boards are flooded with ghost jobs (posted months ago, never filled), scams (fake companies, upfront fees), and misclassified listings (advertised as W2 but actually C2C/1099). Finding legitimate, fresh W2 positions requires manually cross-referencing multiple sources.

## Solution

An automated pipeline that:

1. **Collects** jobs from verified sources (company career pages via Bloomberry, RSS feeds, LinkedIn API)
2. **Normalizes** diverse formats into a single schema
3. **Filters** for employment type (W2 vs C2C), freshness, and legitimacy
4. **Scores** each listing with a trust metric based on multiple signals
5. **Presents** results through a filterable dashboard

## Architecture Decisions

### Why FastAPI (not Flask/Django)?

- **Async-native**: Job fetching hits external APIs — async I/O is critical for performance
- **Automatic OpenAPI docs**: Interactive `/docs` endpoint for free
- **Pydantic integration**: Request validation and response serialization with zero boilerplate
- **Dependency injection**: Clean separation of concerns (DB sessions, Redis, config)

### Why PostgreSQL + Redis (not SQLite)?

- **PostgreSQL JSONB**: Flexible storage for trust score flags without schema changes
- **Full-text search**: Built-in `tsvector` for job description search (Phase 2+)
- **Redis for dedup**: O(1) set membership check for URL hashes — faster than DB lookups
- **Redis for caching**: Cache API responses to avoid hitting the DB on every page load

### Why separate Pydantic models from SQLAlchemy models?

- **API contracts shouldn't leak DB internals**: The API can evolve independently of the DB schema
- **Computed fields**: `trust_level` is derived from `trust_score` at serialization time, not stored
- **Validation**: Pydantic enforces constraints (score range, URL format) that don't belong in the ORM

### Why APScheduler (not Celery)?

- **Single-process simplicity**: This is a personal tool, not a distributed system
- **No broker overhead**: Celery needs a separate message broker (RabbitMQ/Redis); APScheduler runs in-process
- **Cron-like scheduling**: Built-in support for interval and cron triggers

## Data Flow

```
Source APIs/Feeds
    │
    ▼
Source Adapters (normalize to JobCreate schema)
    │
    ▼
Deduplication (SHA-256 URL hash → Redis set check)
    │
    ▼
Filter Pipeline
    ├── Freshness filter (flag >14 days)
    ├── W2 classifier (regex + keyword scoring)
    └── Scam detector (red/green flag analysis)
    │
    ▼
Enrichment Pipeline
    ├── Company verification (LinkedIn/Clearbit lookup)
    ├── Career page validation (does job exist on company.com/careers?)
    └── Trust score computation (weighted sum of all signals)
    │
    ▼
PostgreSQL (persistent storage)
    │
    ▼
FastAPI (REST API with filters + pagination)
    │
    ▼
React Dashboard (interactive filtering, trust badges)
```

## Trust Score Computation

The trust score is a weighted average of independent signals:

| Signal | Weight | Range | Description |
|--------|--------|-------|-------------|
| Source reliability | 0.25 | 0-1 | Career page = 1.0, Bloomberry = 0.8, LinkedIn = 0.6, RSS = 0.4 |
| Company verification | 0.25 | 0-1 | LinkedIn presence, employee count, domain match |
| Freshness | 0.20 | 0-1 | <7 days = 1.0, 7-14 = 0.7, 14-30 = 0.4, >30 = 0.1 |
| Description quality | 0.15 | 0-1 | Specific tech stack, clear role, salary info |
| Contact legitimacy | 0.15 | 0-1 | Company email = 1.0, personal email = 0.2 |

## Title Expansion Strategy

Instead of using an LLM for every search, we use a static synonym map with common IT/engineering title variations:

```python
TITLE_SYNONYMS = {
    "it support": ["help desk", "desktop support", "tech support tier 1", "service desk analyst"],
    "devops engineer": ["sre", "platform engineer", "infrastructure engineer", "cloud engineer"],
    "backend developer": ["backend engineer", "server-side developer", "api developer"],
    "frontend developer": ["frontend engineer", "ui developer", "react developer"],
    "full stack developer": ["full stack engineer", "software engineer"],
    "data engineer": ["data platform engineer", "etl developer", "analytics engineer"],
    "security engineer": ["cybersecurity engineer", "infosec engineer", "security analyst"],
}
```

This can be extended with an LLM in a future phase if the static map proves insufficient.

## Future Considerations

- **Rate limiting**: External API calls need backoff/retry logic
- **Webhook support**: Allow users to get notified when high-trust jobs match their criteria
- **ML scoring**: Train a classifier on user feedback (thumbs up/down) to improve trust scoring
- **Multi-user**: Currently single-user; would need auth + per-user preferences for multi-tenant

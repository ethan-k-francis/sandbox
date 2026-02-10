# Design Notes — Example Go API

## Architecture

This project follows the standard Go project layout with a layered architecture:

```text
┌────────────────────────────────────┐
│         cmd/server/main.go         │  ← Entry point (wiring only)
│   Creates deps, wires routes,      │     No business logic here
│   starts server                    │
├────────────────────────────────────┤
│   middleware/ (logging, auth...)   │  ← Cross-cutting concerns
│   Wraps handlers, runs before/after│     Doesn't know about business logic
├────────────────────────────────────┤
│         handlers/                  │  ← HTTP layer
│   Parse request → call service     │     Knows HTTP, doesn't know storage
│   → write response                 │
├────────────────────────────────────┤
│         service/                   │  ← Business logic layer
│   Validation, rules, orchestration │     Doesn't know about HTTP
├────────────────────────────────────┤
│         models/                    │  ← Data + interfaces
│   Structs, interfaces, no logic    │     Used by all layers
└────────────────────────────────────┘
```

Dependencies flow downward. No layer imports from a layer above it.

## Decisions

| Decision | Choice | Why |
|---|---|---|
| HTTP router | `net/http` (stdlib) | Simple, no dependencies, Go 1.22+ has path params |
| Middleware | Hand-rolled | Only need logging for now; add chi if it grows |
| Data storage | In-memory slice | Example only; swap for Postgres via repository interface |
| Config | Environment variables | Twelve-Factor App, works in Docker/K8s |
| Testing | `testing` + `httptest` | Go stdlib is excellent, no framework needed |
| Dependency injection | Constructor injection | Simple, explicit, testable |

## Future Additions

When the project grows, add these in order:

1. **Database** — Replace in-memory slice with Postgres via `pgx`
2. **Repository pattern** — Interface between service and database
3. **Structured logging** — Replace `log` with `slog` (stdlib) or `zerolog`
4. **Authentication** — JWT middleware for protected routes
5. **Docker** — Dockerfile + docker-compose for local development
6. **CI** — GitHub Actions for build, test, lint on every PR

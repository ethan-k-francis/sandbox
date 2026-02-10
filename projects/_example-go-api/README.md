# Example Go HTTP API

A reference project showing the standard structure for a Go HTTP service.
Use this as a template when starting a new Go project — HTTP API, CLI tool,
system utility, or concurrent worker.

**This is not a real API** — it's a documented skeleton showing where everything goes.

## Project Structure

```text
_example-go-api/
├── README.md                   # You're reading it
├── go.mod                      # Module path and dependency versions
├── Makefile                    # Build, run, test, lint commands
├── cmd/
│   └── server/
│       └── main.go             # Entry point — wires dependencies, starts server
├── internal/
│   ├── handlers/
│   │   └── health.go           # HTTP route handlers (request → response)
│   ├── middleware/
│   │   └── logging.go          # HTTP middleware (runs before/after handlers)
│   ├── models/
│   │   └── item.go             # Data structures (structs, interfaces)
│   ├── service/
│   │   └── item_service.go     # Business logic (use cases, orchestration)
│   └── config/
│       └── config.go           # Configuration loading from env vars
├── tests/
│   └── integration_test.go     # Integration tests (spin up real server)
└── docs/
    └── DESIGN.md               # Design decisions and architecture notes
```

## Key Concepts

### `cmd/` — Entry Points

Go convention: each binary gets a folder under `cmd/`. The folder name becomes the binary name.

```text
cmd/
├── server/main.go     → builds to `./bin/server`
├── worker/main.go     → builds to `./bin/worker`    (if you add a background worker)
└── migrate/main.go    → builds to `./bin/migrate`   (if you add DB migrations)
```

`main.go` should be minimal — create dependencies, wire them together, start the server.
All real logic lives in `internal/`.

### `internal/` — Private Application Code

Go enforces `internal/` visibility: packages inside `internal/` can only be imported by
code in the parent module. Other Go modules literally cannot import them. This prevents
external projects from depending on your internal implementation details.

| Package | Responsibility | Depends On |
|---|---|---|
| `handlers/` | Parse HTTP requests, call service, return HTTP responses | `service/`, `models/` |
| `middleware/` | Cross-cutting concerns (logging, auth, CORS, rate limiting) | Nothing |
| `models/` | Data structures and interfaces (no logic) | Nothing |
| `service/` | Business logic — the "what the app does" | `models/` |
| `config/` | Load configuration from environment variables | Nothing |

Dependencies flow inward: handlers → service → models. Nothing imports handlers.

### `pkg/` — Public Library Code (Not Included)

If you want other Go projects to import your code, put it in `pkg/`. Most applications
don't need this — it's for libraries and shared utilities. Only create `pkg/` when you
have a real use case for exporting code.

### Where Do Tests Go?

Go has two conventions, both used here:

1. **Unit tests** — same directory as the code, named `*_test.go`
   - `internal/service/item_service_test.go` tests `item_service.go`
   - Tests the package in isolation, can access unexported functions

2. **Integration tests** — `tests/` directory
   - Spin up a real HTTP server, make real requests
   - Test the full request → handler → service → response flow

## How to Set Up

```bash
cd projects/_example-go-api

# Download dependencies (reads go.mod)
go mod tidy

# Build the binary
go build -o bin/server ./cmd/server

# Run the server
./bin/server

# Or build and run in one step
go run ./cmd/server

# Run all tests
go test ./...

# Run tests with coverage
go test -cover ./...

# Run linter (install: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest)
golangci-lint run

# Or use the Makefile
make build
make run
make test
make lint
```

## How to Adapt This Template

1. Update `go.mod` with your actual module path
2. Rename the `cmd/server/` binary if it's not an HTTP server
3. Replace the example handlers/service with your actual logic
4. Add real models to `models/`
5. Write tests as you go (Go's `testing` package is excellent — no framework needed)

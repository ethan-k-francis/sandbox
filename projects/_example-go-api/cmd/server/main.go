// =============================================================================
// main.go — Server Entry Point
// =============================================================================
// This is where the program starts. Its only job is to:
//   1. Load configuration from environment
//   2. Create dependencies (services, handlers)
//   3. Wire up HTTP routes
//   4. Start the server and handle graceful shutdown
//
// main.go should be thin — all real logic lives in internal/.
// Think of main.go as the "wiring diagram" that connects the pieces.
//
// Graceful shutdown:
//   When the server gets SIGINT (Ctrl+C) or SIGTERM (kill), it should:
//   1. Stop accepting new connections
//   2. Wait for in-flight requests to finish (with a timeout)
//   3. Clean up resources (close DB connections, flush logs)
//   4. Exit cleanly
//   This prevents dropped requests during deploys.
// =============================================================================

package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/ethan-k-francis/sandbox/projects/_example-go-api/internal/config"
	"github.com/ethan-k-francis/sandbox/projects/_example-go-api/internal/handlers"
	"github.com/ethan-k-francis/sandbox/projects/_example-go-api/internal/middleware"
	"github.com/ethan-k-francis/sandbox/projects/_example-go-api/internal/service"
)

func main() {
	// Load configuration from environment variables
	cfg := config.Load()

	// Create service layer (business logic)
	itemSvc := service.NewItemService()

	// Create HTTP handler with injected dependencies
	// This is dependency injection: main.go creates the service and passes
	// it to the handler. The handler doesn't create its own dependencies.
	itemHandler := handlers.NewItemHandler(itemSvc)
	healthHandler := handlers.NewHealthHandler()

	// Set up HTTP routes using the standard library's ServeMux
	// For larger APIs, consider chi or gorilla/mux for route parameters
	mux := http.NewServeMux()

	// Health check endpoint — used by load balancers and Kubernetes probes
	mux.HandleFunc("GET /health", healthHandler.Health)

	// Item CRUD endpoints
	mux.HandleFunc("GET /items", itemHandler.List)
	mux.HandleFunc("POST /items", itemHandler.Create)

	// Wrap all routes with middleware (logging, recovery, etc.)
	// Middleware runs in order: first added = outermost (runs first)
	handler := middleware.Logging(mux)

	// Create the HTTP server with timeouts
	// ALWAYS set timeouts — without them, a slow client can hold a connection
	// open forever, eventually exhausting server resources (DoS)
	server := &http.Server{
		Addr:         ":" + cfg.Port,
		Handler:      handler,
		ReadTimeout:  5 * time.Second,   // Max time to read request (headers + body)
		WriteTimeout: 10 * time.Second,  // Max time to write response
		IdleTimeout:  120 * time.Second, // Max time to keep idle connection open
	}

	// Start server in a goroutine so we can listen for shutdown signals
	go func() {
		log.Printf("Server starting on :%s", cfg.Port)
		if err := server.ListenAndServe(); err != http.ErrServerClosed {
			log.Fatalf("Server error: %v", err)
		}
	}()

	// Wait for shutdown signal (Ctrl+C or kill)
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit // Block until signal received

	log.Println("Shutting down server...")

	// Give in-flight requests up to 30 seconds to finish
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server stopped cleanly")
}

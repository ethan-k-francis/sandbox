// =============================================================================
// integration_test.go — HTTP Integration Tests
// =============================================================================
// Tests the full request → handler → service → response flow by spinning up
// a real HTTP server and making real HTTP requests.
//
// Why integration tests?
//   Unit tests (testing functions in isolation) catch logic bugs.
//   Integration tests catch wiring bugs: "did I connect the handler to the
//   right route?", "does JSON serialization work end-to-end?", "does the
//   middleware run?"
//
// Go's httptest package:
//   httptest.NewServer() creates a real HTTP server on a random port.
//   You make real HTTP requests to it. No mocking the HTTP layer.
//   This is a Go superpower — integration tests are trivial to write.
//
// Test structure:
//   1. Create dependencies (service, handlers)
//   2. Start a test server
//   3. Make HTTP requests
//   4. Assert on status code and response body
//   5. Server shuts down automatically when the test ends
// =============================================================================

package tests

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/ethan-k-francis/sandbox/projects/_example-go-api/internal/handlers"
	"github.com/ethan-k-francis/sandbox/projects/_example-go-api/internal/service"
)

// setupTestServer creates an HTTP test server with all routes wired up.
// Each test gets its own server with fresh state (tests don't interfere).
func setupTestServer(t *testing.T) *httptest.Server {
	t.Helper() // Marks this as a helper — errors report the caller's line number

	itemSvc := service.NewItemService()
	itemHandler := handlers.NewItemHandler(itemSvc)
	healthHandler := handlers.NewHealthHandler()

	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", healthHandler.Health)
	mux.HandleFunc("GET /items", itemHandler.List)
	mux.HandleFunc("POST /items", itemHandler.Create)

	return httptest.NewServer(mux)
}

func TestHealthEndpoint(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Make a GET request to /health
	resp, err := http.Get(server.URL + "/health")
	if err != nil {
		t.Fatalf("Failed to make request: %v", err)
	}
	defer resp.Body.Close()

	// Should return 200 OK
	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}

	// Should return JSON with status "ok"
	var body map[string]string
	if err := json.NewDecoder(resp.Body).Decode(&body); err != nil {
		t.Fatalf("Failed to decode response body: %v", err)
	}
	if body["status"] != "ok" {
		t.Errorf("Expected status 'ok', got '%s'", body["status"])
	}
}

func TestCreateAndListItems(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Create an item via POST
	createBody := `{"name": "Test Item", "description": "A test item"}`
	resp, err := http.Post(server.URL+"/items", "application/json", strings.NewReader(createBody))
	if err != nil {
		t.Fatalf("Failed to create item: %v", err)
	}
	defer resp.Body.Close()

	// Should return 201 Created
	if resp.StatusCode != http.StatusCreated {
		t.Errorf("Expected status 201, got %d", resp.StatusCode)
	}

	// List items via GET
	resp, err = http.Get(server.URL + "/items")
	if err != nil {
		t.Fatalf("Failed to list items: %v", err)
	}
	defer resp.Body.Close()

	// Should return 200 with one item
	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected status 200, got %d", resp.StatusCode)
	}

	var items []map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&items); err != nil {
		t.Fatalf("Failed to decode items response: %v", err)
	}
	if len(items) != 1 {
		t.Errorf("Expected 1 item, got %d", len(items))
	}
	if items[0]["name"] != "Test Item" {
		t.Errorf("Expected item name 'Test Item', got '%s'", items[0]["name"])
	}
}

func TestCreateItemValidation(t *testing.T) {
	server := setupTestServer(t)
	defer server.Close()

	// Try to create an item without a name
	createBody := `{"description": "Missing name"}`
	resp, err := http.Post(server.URL+"/items", "application/json", strings.NewReader(createBody))
	if err != nil {
		t.Fatalf("Failed to make request: %v", err)
	}
	defer resp.Body.Close()

	// Should return 400 Bad Request
	if resp.StatusCode != http.StatusBadRequest {
		t.Errorf("Expected status 400, got %d", resp.StatusCode)
	}
}

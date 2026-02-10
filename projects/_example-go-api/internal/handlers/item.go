// =============================================================================
// item.go — Item HTTP Handlers
// =============================================================================
// Handles HTTP requests for item CRUD operations. Each handler method:
//   1. Parses the HTTP request (read body, validate input)
//   2. Calls the service layer (business logic)
//   3. Writes the HTTP response (status code, JSON body)
//
// Handlers should NOT contain business logic — that belongs in the service.
// Handlers are the translation layer between HTTP and your application.
//
// Error handling pattern:
//   - Client errors (bad input): 400 Bad Request with error message
//   - Not found: 404 Not Found
//   - Server errors (bugs, DB down): 500 Internal Server Error
//   - Always return JSON error responses, not plain text
// =============================================================================

package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/ethan-k-francis/sandbox/projects/_example-go-api/internal/models"
)

// ItemHandler handles HTTP requests for items.
// It depends on the ItemService interface, not the concrete implementation.
// This means tests can inject a mock service.
type ItemHandler struct {
	service models.ItemService
}

// NewItemHandler creates an ItemHandler with the given service.
// This is constructor injection — dependencies are passed in, not created here.
func NewItemHandler(svc models.ItemService) *ItemHandler {
	return &ItemHandler{service: svc}
}

// errorResponse is a standard JSON error body.
type errorResponse struct {
	Error string `json:"error"`
}

// List returns all items as JSON.
// GET /items → 200 [{"id": "...", "name": "...", ...}, ...]
func (h *ItemHandler) List(w http.ResponseWriter, r *http.Request) {
	items, err := h.service.List()
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(errorResponse{Error: "failed to list items"})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(items)
}

// Create adds a new item from the JSON request body.
// POST /items {"name": "...", "description": "..."} → 201 {"id": "...", ...}
func (h *ItemHandler) Create(w http.ResponseWriter, r *http.Request) {
	var req models.CreateItemRequest

	// Decode the JSON request body into our struct
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(errorResponse{Error: "invalid JSON body"})
		return
	}

	// Validate required fields
	if req.Name == "" {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(errorResponse{Error: "name is required"})
		return
	}

	// Call service to create the item
	item, err := h.service.Create(req)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(errorResponse{Error: "failed to create item"})
		return
	}

	// Return the created item with 201 Created status
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(item)
}

// =============================================================================
// item_service.go — Item Business Logic
// =============================================================================
// Implements the ItemService interface with the actual business logic.
// This layer sits between handlers (HTTP) and data storage (database/memory).
//
// Why a service layer?
//   Handlers know about HTTP (requests, responses, status codes).
//   The service knows about business rules (validation, authorization, workflows).
//   The data layer knows about storage (SQL queries, file I/O).
//
//   This separation means:
//   - Business rules are testable without HTTP
//   - You can add a CLI or gRPC interface that calls the same service
//   - Swapping storage (in-memory → Postgres) only changes the data layer
//
// This example uses an in-memory slice for storage. In a real project, you'd
// inject a repository interface that wraps a database connection.
// =============================================================================

package service

import (
	"fmt"
	"sync"
	"time"

	"github.com/ethan-k-francis/sandbox/projects/_example-go-api/internal/models"
)

// itemService implements models.ItemService with in-memory storage.
// In production, this would hold a database connection pool instead of a slice.
type itemService struct {
	mu    sync.RWMutex   // Protects items from concurrent access (goroutine-safe)
	items []models.Item  // In-memory storage (replaced by DB in production)
	nextID int           // Simple auto-increment ID (replaced by UUID in production)
}

// NewItemService creates a new ItemService with empty in-memory storage.
// In production, this would take a *sql.DB or repository interface as a parameter.
func NewItemService() models.ItemService {
	return &itemService{
		items: make([]models.Item, 0), // Pre-allocate empty slice (not nil)
	}
}

// List returns all items.
// Uses a read lock (RLock) so multiple goroutines can read simultaneously.
func (s *itemService) List() ([]models.Item, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	// Return a copy to prevent callers from mutating our internal state
	result := make([]models.Item, len(s.items))
	copy(result, s.items)
	return result, nil
}

// Create adds a new item and returns it with a generated ID and timestamp.
// Uses a write lock (Lock) so only one goroutine can create at a time.
func (s *itemService) Create(req models.CreateItemRequest) (*models.Item, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.nextID++
	item := models.Item{
		ID:          fmt.Sprintf("item-%d", s.nextID),
		Name:        req.Name,
		Description: req.Description,
		CreatedAt:   time.Now(),
	}

	s.items = append(s.items, item)
	return &item, nil
}

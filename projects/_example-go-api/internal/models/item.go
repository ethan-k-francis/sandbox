// =============================================================================
// item.go — Item Data Model
// =============================================================================
// Defines the data structures used across the application. Models are pure
// data — no methods with side effects, no database calls, no HTTP awareness.
//
// Struct tags:
//   `json:"name"` controls how the field is named in JSON serialization.
//   Without tags, Go uses the field name as-is (PascalCase), which doesn't
//   match the conventional camelCase or snake_case used in APIs.
//
// Why define interfaces here?
//   The service interface defines "what the service can do" without saying
//   how it does it. Handlers depend on the interface, not the concrete
//   implementation. This means:
//   - Tests can use a mock service (no real database)
//   - You can swap implementations (in-memory → PostgreSQL) without
//     changing the handler code
//   - This is the Dependency Inversion Principle
// =============================================================================

package models

import "time"

// Item represents a single item in the system.
// This is the core domain type — everything revolves around it.
type Item struct {
	ID          string    `json:"id"`           // Unique identifier (UUID)
	Name        string    `json:"name"`         // Display name
	Description string    `json:"description"`  // Optional description
	CreatedAt   time.Time `json:"created_at"`   // When the item was created
}

// CreateItemRequest is the payload for creating a new item.
// Separate from Item because the client doesn't provide ID or CreatedAt —
// the server generates those.
type CreateItemRequest struct {
	Name        string `json:"name"`        // Required: item name
	Description string `json:"description"` // Optional: item description
}

// ItemService defines the business operations for items.
// Handlers depend on this interface, not the concrete implementation.
type ItemService interface {
	List() ([]Item, error)
	Create(req CreateItemRequest) (*Item, error)
}

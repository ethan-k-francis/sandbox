// =============================================================================
// health.go — Health Check Handler
// =============================================================================
// Provides a /health endpoint for infrastructure to probe.
//
// Who calls /health?
//   - Kubernetes liveness/readiness probes (restarts unhealthy pods)
//   - Load balancers (routes traffic away from unhealthy instances)
//   - Monitoring systems (alerts when a service is down)
//   - Developers (quick "is it running?" check)
//
// What to return:
//   - 200 OK + JSON body if the service is healthy
//   - 503 Service Unavailable if the service can't serve requests
//     (e.g., database is unreachable, critical dependency is down)
//
// For a simple service, just returning 200 is fine. For production services
// with databases or external dependencies, check those connections and
// report their status in the response body.
// =============================================================================

package handlers

import (
	"encoding/json"
	"net/http"
)

// HealthHandler handles health check requests.
// It's a struct (not a bare function) so we can add dependencies later
// (e.g., a DB connection to check in the health response).
type HealthHandler struct{}

// NewHealthHandler creates a new HealthHandler.
func NewHealthHandler() *HealthHandler {
	return &HealthHandler{}
}

// healthResponse is the JSON body returned by the health endpoint.
type healthResponse struct {
	Status string `json:"status"` // "ok" or "degraded"
}

// Health returns the current health status of the service.
// GET /health → 200 {"status": "ok"}
func (h *HealthHandler) Health(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)

	resp := healthResponse{Status: "ok"}
	json.NewEncoder(w).Encode(resp)
}

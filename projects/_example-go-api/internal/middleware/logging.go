// =============================================================================
// logging.go — HTTP Request Logging Middleware
// =============================================================================
// Middleware wraps an HTTP handler and runs logic before and/or after the
// handler executes. It's the Go equivalent of decorators or interceptors.
//
// Common middleware:
//   - Logging:    Log every request (method, path, status, duration)
//   - Recovery:   Catch panics so one bad request doesn't crash the server
//   - Auth:       Check JWT/session before allowing access
//   - CORS:       Add Cross-Origin headers for browser requests
//   - RateLimit:  Throttle requests per IP/user
//
// Middleware pattern in Go:
//   func MyMiddleware(next http.Handler) http.Handler {
//       return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
//           // Before handler
//           next.ServeHTTP(w, r)  // Call the actual handler
//           // After handler
//       })
//   }
//
// Middleware chains: Logging(Auth(Recovery(yourHandler)))
//   Request flows: Logging → Auth → Recovery → Handler → Recovery → Auth → Logging
// =============================================================================

package middleware

import (
	"log"
	"net/http"
	"time"
)

// responseWriter wraps http.ResponseWriter to capture the status code.
// The standard ResponseWriter doesn't expose the status code after WriteHeader(),
// so we wrap it to record it for logging.
type responseWriter struct {
	http.ResponseWriter
	statusCode int
}

// WriteHeader captures the status code before passing it to the real ResponseWriter.
func (rw *responseWriter) WriteHeader(code int) {
	rw.statusCode = code
	rw.ResponseWriter.WriteHeader(code)
}

// Logging returns middleware that logs every HTTP request.
// Log format: METHOD /path → STATUS (duration)
// Example: GET /health → 200 (1.23ms)
func Logging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		// Wrap the ResponseWriter to capture the status code
		wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

		// Call the next handler in the chain
		next.ServeHTTP(wrapped, r)

		// Log after the handler completes
		duration := time.Since(start)
		log.Printf("%s %s → %d (%s)",
			r.Method,
			r.URL.Path,
			wrapped.statusCode,
			duration.Round(time.Microsecond),
		)
	})
}

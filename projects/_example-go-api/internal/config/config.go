// =============================================================================
// config.go — Configuration Loading
// =============================================================================
// Loads application configuration from environment variables with defaults.
//
// Why environment variables?
//   - Works everywhere: local dev, Docker, Kubernetes, CI/CD
//   - No config files to manage per environment
//   - Follows the Twelve-Factor App methodology (https://12factor.net/config)
//   - Secrets never end up in code or config files
//
// Configuration hierarchy:
//   1. Environment variable (highest priority — runtime override)
//   2. Default value in code (safe fallback)
//
// Naming convention:
//   APP_PORT, APP_LOG_LEVEL, APP_DB_URL
//   Prefix with the app name to avoid collisions with other env vars.
// =============================================================================

package config

import "os"

// Config holds all application configuration.
// Each field has a sensible default that works for local development.
type Config struct {
	// Port the HTTP server listens on.
	// Default: 8080 (standard non-privileged HTTP port)
	Port string

	// LogLevel controls verbosity: "debug", "info", "warn", "error"
	// Default: "info" (shows normal operations, not noisy)
	LogLevel string

	// Environment name: "development", "staging", "production"
	// Used to adjust behavior (e.g., pretty vs JSON logs, debug endpoints)
	Environment string
}

// Load reads configuration from environment variables, falling back to defaults.
// Call this once in main() and pass the Config to anything that needs it.
func Load() *Config {
	return &Config{
		Port:        getEnv("APP_PORT", "8080"),
		LogLevel:    getEnv("APP_LOG_LEVEL", "info"),
		Environment: getEnv("APP_ENVIRONMENT", "development"),
	}
}

// getEnv reads an environment variable or returns a default value.
// This is a tiny helper to avoid repeating the os.Getenv + fallback pattern.
func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}

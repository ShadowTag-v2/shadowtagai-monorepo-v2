// infra/shield/main_test.go
// Cloud Run Shield Test — validates security headers, rate limiting,
// and health endpoint behavior against the live Cloud Run deployment.
package shield

import (
	"encoding/json"
	"io"
	"net/http"
	"strings"
	"testing"
	"time"
)

const baseURL = "https://counselconduit-767252945109.us-central1.run.app"

// TestHealthEndpoint verifies the health check returns a valid JSON response.
func TestHealthEndpoint(t *testing.T) {
	resp, err := http.Get(baseURL + "/health")
	if err != nil {
		t.Fatalf("Failed to reach health endpoint: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected 200, got %d", resp.StatusCode)
	}

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		t.Fatalf("Invalid JSON response: %v", err)
	}

	if result["status"] != "healthy" {
		t.Errorf("Expected status=healthy, got %v", result["status"])
	}
}

// TestSecurityHeaders validates Cor.30 R31 security headers.
func TestSecurityHeaders(t *testing.T) {
	resp, err := http.Get(baseURL + "/")
	if err != nil {
		t.Fatalf("Failed to reach root: %v", err)
	}
	defer resp.Body.Close()

	headers := map[string]string{
		"Content-Security-Policy":   "default-src 'self'",
		"Strict-Transport-Security": "max-age=63072000",
		"X-Content-Type-Options":    "nosniff",
		"X-Frame-Options":           "DENY",
		"Referrer-Policy":           "strict-origin-when-cross-origin",
		"Permissions-Policy":        "camera=()",
	}

	for header, expectedSubstr := range headers {
		val := resp.Header.Get(header)
		if val == "" {
			t.Errorf("Missing security header: %s", header)
		} else if !strings.Contains(val, expectedSubstr) {
			t.Errorf("Header %s does not contain %q, got: %s", header, expectedSubstr, val)
		}
	}
}

// TestRateLimitHeaders verifies rate limit headers are present.
func TestRateLimitHeaders(t *testing.T) {
	resp, err := http.Get(baseURL + "/")
	if err != nil {
		t.Fatalf("Failed to reach root: %v", err)
	}
	defer resp.Body.Close()

	requiredHeaders := []string{"X-Ratelimit-Limit", "X-Ratelimit-Remaining", "X-Ratelimit-Reset"}
	for _, h := range requiredHeaders {
		if resp.Header.Get(h) == "" {
			t.Errorf("Missing rate limit header: %s", h)
		}
	}
}

// TestDocsDisabledInProduction ensures /docs is not exposed in production.
func TestDocsDisabledInProduction(t *testing.T) {
	resp, err := http.Get(baseURL + "/docs")
	if err != nil {
		t.Fatalf("Failed to reach /docs: %v", err)
	}
	defer resp.Body.Close()

	// In production, /docs should return 404 (disabled)
	if resp.StatusCode == http.StatusOK {
		t.Error("/docs should be disabled in production but returned 200")
	}
}

// TestOpaqueErrorResponse verifies that errors don't leak stack traces.
func TestOpaqueErrorResponse(t *testing.T) {
	resp, err := http.Get(baseURL + "/nonexistent-route-12345")
	if err != nil {
		t.Fatalf("Failed to reach nonexistent route: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	bodyStr := string(body)

	// Must NOT contain stack traces or internal paths
	forbidden := []string{"Traceback", "/app/", "/usr/local/lib/", "File \""}
	for _, f := range forbidden {
		if strings.Contains(bodyStr, f) {
			t.Errorf("Error response leaked internal info: contains %q", f)
		}
	}
}

// TestResponseLatency checks that the health endpoint responds within 5s.
func TestResponseLatency(t *testing.T) {
	start := time.Now()
	resp, err := http.Get(baseURL + "/health")
	elapsed := time.Since(start)

	if err != nil {
		t.Fatalf("Failed to reach health: %v", err)
	}
	defer resp.Body.Close()

	if elapsed > 5*time.Second {
		t.Errorf("Health endpoint took %v (max 5s)", elapsed)
	}
}

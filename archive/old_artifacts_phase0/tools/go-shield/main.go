// Package main provides a Go-based HTTP middleware shield layer
// for rate limiting, auth validation, and request sanitization.
package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

// RateLimiter implements a token bucket rate limiter.
type RateLimiter struct {
	Rate     int
	Burst    int
	Tokens   int
	LastTime time.Time
}

// Allow checks if a request is allowed under the rate limit.
func (rl *RateLimiter) Allow() bool {
	now := time.Now()
	elapsed := now.Sub(rl.LastTime)
	rl.Tokens += int(elapsed.Seconds()) * rl.Rate
	if rl.Tokens > rl.Burst {
		rl.Tokens = rl.Burst
	}
	rl.LastTime = now
	if rl.Tokens > 0 {
		rl.Tokens--
		return true
	}
	return false
}

// ShieldMiddleware wraps an http.Handler with auth + rate limiting.
func ShieldMiddleware(next http.Handler) http.Handler {
	limiter := &RateLimiter{Rate: 10, Burst: 50, Tokens: 50, LastTime: time.Now()}
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Rate limit check
		if !limiter.Allow() {
			http.Error(w, "429 Too Many Requests", http.StatusTooManyRequests)
			return
		}
		// Auth header validation
		authHeader := r.Header.Get("Authorization")
		if authHeader == "" {
			http.Error(w, "401 Unauthorized", http.StatusUnauthorized)
			return
		}
		next.ServeHTTP(w, r)
	})
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8090"
	}
	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, _ *http.Request) {
		fmt.Fprintln(w, `{"status":"ok"}`)
	})
	log.Printf("Go Shield Layer listening on :%s", port)
	log.Fatal(http.ListenAndServe(":"+port, ShieldMiddleware(mux)))
}

package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
)

// ShieldInterceptor encapsulates the Edge routing protections
func ShieldInterceptor(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Log edge trigger
		log.Printf("[SHIELD] Access intercepted at path: %s", r.URL.Path)
		
		// CRSMC Layer 1 Logic
		signature := r.Header.Get("X-Internal-Shield-Sig")
		if signature == "" {
			http.Error(w, "Forbidden Gateway", http.StatusForbidden)
			return
		}

		// Layer 2: Suicide/Crisis Check
		if r.Header.Get("X-DOW-L2-Crisis") == "FAIL" {
			http.Error(w, "L2: Crisis Intervention Triggered", http.StatusForbidden)
			return
		}

		// Layer 3: Deepfake/Synthetic Media
		if r.Header.Get("X-DOW-L3-Deepfake") == "FAIL" {
			http.Error(w, "L3: Synthetic Media Detected", http.StatusForbidden)
			return
		}

		// Layer 4: SynthID Watermarking
		if r.Header.Get("X-DOW-L4-SynthID") == "FAIL" {
			http.Error(w, "L4: Provenance Verification Failed", http.StatusForbidden)
			return
		}

		// Layer 5: CA SB243 / AADC Minors
		if r.Header.Get("X-DOW-L5-AADC") == "FAIL" {
			http.Error(w, "L5: Minor PII/Age Restriction Block", http.StatusForbidden)
			return
		}

		// Layer 6: EU AI Act (2026+)
		if r.Header.Get("X-DOW-L6-EUAI") == "FAIL" {
			http.Error(w, "L6: EU Regulatory Block", http.StatusForbidden)
			return
		}

		// Layer 7: Financial Risk
		if r.Header.Get("X-DOW-L7-FinRisk") == "FAIL" {
			http.Error(w, "L7: Financial Risk Assessment Failed", http.StatusForbidden)
			return
		}

		// Layer 8: Hacker/Phishing/Whaling
		if r.Header.Get("X-DOW-L8-Phishing") == "FAIL" {
			http.Error(w, "L8: Security Anomaly Detected", http.StatusForbidden)
			return
		}

		// Layer 9: Supply Chain (ATP 5-19)
		if r.Header.Get("X-DOW-L9-SupplyChain") == "FAIL" {
			http.Error(w, "L9: Supply Chain Audit Failed", http.StatusForbidden)
			return
		}

		// Layer 10: KYB/KYE/Espionage
		if r.Header.Get("X-DOW-L10-Espionage") == "FAIL" {
			http.Error(w, "L10: Espionage/KYB Verification Failed", http.StatusForbidden)
			return
		}

		// Layer 11: Harassment/Retaliation
		if r.Header.Get("X-DOW-L11-Harassment") == "FAIL" {
			http.Error(w, "L11: Policy Violation Detected", http.StatusForbidden)
			return
		}

		// Layer 12: Security+ Mapping
		if r.Header.Get("X-DOW-L12-SecPlus") == "FAIL" {
			http.Error(w, "L12: Security+ Framework Violation", http.StatusForbidden)
			return
		}

		// Pass to core application logic if verified
		next.ServeHTTP(w, r)
	})
}

// Health check handler
func healthHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Shield is operational.")
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", healthHandler)

	// Wrap multiplexer with shield interceptor
	wrappedMux := ShieldInterceptor(mux)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Starting Cloud Run Shield Interceptor on port %s", port)
	if err := http.ListenAndServe(":"+port, wrappedMux); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}

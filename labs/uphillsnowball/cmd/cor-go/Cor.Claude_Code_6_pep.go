// cmd/cor-go/Cor.Claude_Code_6_pep.go
//
// Cor.Go — Zero Trust Architecture Kernel & Wet Fleece Stripe Gate
//
// The ZTA Policy Enforcement Point (PEP) for every inbound request.
// Three gates, in order:
//   1. WET FLEECE: Sub-millisecond Redis cache check of Stripe subscription.
//      If billing_status != "active", return HTTP 402. Zero compute expended.
//   2. JUDGE 6.1 PEP: Payload content analysis for RKILL/KICKBACK triggers.
//   3. TEMPORAL DISPATCH: If cleared, dispatch the durable workflow.
//
// The Go kernel exists because sub-millisecond latency at ingress cannot
// be achieved in Python. The Wet Fleece gate must be faster than the
// customer's patience.

package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/redis/go-redis/v9"
	"go.temporal.io/sdk/client"
)

var (
	rdb            *redis.Client
	temporalClient client.Client
)

// Request payload structure
type ZTARequest struct {
	TenantID string `json:"tenant_id"`
	Payload  string `json:"payload"`
	Hash     string `json:"hash"`
	AgentID  string `json:"agent_id"`
	Type     string `json:"type"`
}

// Response structure
type ZTAResponse struct {
	Status     string `json:"status"`
	ReasonCode string `json:"reason_code,omitempty"`
	Reason     string `json:"reason,omitempty"`
	WorkflowID string `json:"workflow_id,omitempty"`
}

// verifyWetFleece checks the Stripe subscription cache.
// Sub-millisecond lookup. Updated async by Stripe webhooks.
// If the cache returns anything other than "active", the customer
// is not paying and receives HTTP 402 immediately.
func verifyWetFleece(tenantID string) bool {
	status, err := rdb.Get(context.Background(), "billing:"+tenantID).Result()
	return err == nil && status == "active"
}

// evaluateRisk runs the J-6 content heuristic scan.
// This is the fast-path PEP check. Full AST analysis happens
// downstream in the Python activities.
func evaluateRisk(payload string) string {
	text := strings.ToUpper(payload)

	// RKILL triggers: immediate termination, no appeal
	rkillPatterns := []string{
		"DROP TABLE", "EXFILTRATE", "DELETE ALL", "TRUNCATE",
		"BYPASS SECURITY", "IGNORE INSTRUCTIONS",
	}
	for _, pattern := range rkillPatterns {
		if strings.Contains(text, pattern) {
			return "RKILL"
		}
	}

	// KICKBACK triggers: UPL/bias detection
	kickbackPatterns := []string{
		"YOU SHOULD SUE", "DIAGNOSE THIS PATIENT",
		"PRESCRIBE MEDICATION", "FILE A LAWSUIT",
		"LEGAL ADVICE", "MEDICAL DIAGNOSIS",
	}
	for _, pattern := range kickbackPatterns {
		if strings.Contains(text, pattern) {
			return "KICKBACK"
		}
	}

	return "CLEARED"
}

// pepMiddleware is the main ZTA Policy Enforcement Point handler.
func pepMiddleware(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, `{"status": "METHOD_NOT_ALLOWED"}`, http.StatusMethodNotAllowed)
		return
	}

	var req ZTARequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, `{"status": "BAD_REQUEST"}`, http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")

	// ── GATE 1: WET FLEECE (Stripe billing check) ──────────
	if !verifyWetFleece(req.TenantID) {
		w.WriteHeader(http.StatusPaymentRequired) // 402
		json.NewEncoder(w).Encode(ZTAResponse{
			Status:     "PAYMENT_REQUIRED",
			ReasonCode: "WET_FLEECE",
			Reason:     "Invoice Past Due. Zero compute authorized.",
		})
		return
	}

	// ── GATE 2: JUDGE 6.1 PEP (content analysis) ──────────
	riskStatus := evaluateRisk(req.Payload)

	if riskStatus == "RKILL" {
		w.WriteHeader(http.StatusLocked) // 423
		json.NewEncoder(w).Encode(ZTAResponse{
			Status:     "RKILL",
			ReasonCode: "RKILL_EXECUTED",
			Reason:     "Payload contains prohibited patterns. Session terminated.",
		})
		return
	}

	if riskStatus == "KICKBACK" {
		w.WriteHeader(http.StatusNotAcceptable) // 406
		json.NewEncoder(w).Encode(ZTAResponse{
			Status:     "KICKBACK",
			ReasonCode: "UPL_DETECTED",
			Reason:     "Unauthorized Practice detected. Prescriptive content blocked.",
		})
		return
	}

	// ── GATE 3: TEMPORAL DISPATCH ──────────────────────────
	workflowID := "MDO_CAMPAIGN_" + req.Hash
	_, err := temporalClient.ExecuteWorkflow(
		context.Background(),
		client.StartWorkflowOptions{
			ID:        workflowID,
			TaskQueue: "PNKLN_JTF_QUEUE",
		},
		"MultiDomainTheaterCampaign",
		req,
	)

	if err != nil {
		log.Printf("ERROR: Temporal dispatch failed: %v", err)
		http.Error(w, `{"status": "INTERNAL_ERROR"}`, http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusAccepted) // 202
	json.NewEncoder(w).Encode(ZTAResponse{
		Status:     "DISPATCHED",
		WorkflowID: workflowID,
	})
}

// healthCheck returns 200 if the service is alive.
func healthCheck(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"status": "ALIVE", "model": "gemini-3.1-flash-lite-preview-thinking"}`))
}

func main() {
	// Initialize Redis for Wet Fleece billing cache
	redisAddr := os.Getenv("REDIS_ADDR")
	if redisAddr == "" {
		redisAddr = "localhost:6379"
	}
	rdb = redis.NewClient(&redis.Options{Addr: redisAddr})

	// Initialize Temporal client
	var err error
	temporalClient, err = client.Dial(client.Options{})
	if err != nil {
		log.Fatalf("FATAL: Cannot connect to Temporal: %v", err)
	}
	defer temporalClient.Close()

	// Routes
	http.HandleFunc("/api/v5/zta/evaluate", pepMiddleware)
	http.HandleFunc("/healthz", healthCheck)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("🛡️ Cor.Go ZTA Kernel starting on :%s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

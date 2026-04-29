// cmd/gideon-go/shield1_ingress.go
// ============================================================================
// Cor.Go Shield 1 — Fast-Path Federal Ingress & XML Coordinator Push
// ============================================================================
// Block 3 of the Ex Toto Omni-Compile (Gideon OS Architecture)
// Invariant 5: SERVERLESS PURITY & FEDERAL SUPREMACY
// ============================================================================
package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strings"

	"cloud.google.com/go/pubsub"
)

// ActionPayload represents an incoming action to be evaluated for federal risk.
type ActionPayload struct {
	TenantID string `json:"tenant_id"`
	UserID   string `json:"user_id"`
	Intent   string `json:"intent"`
	RawCode  string `json:"raw_code"`
}

var pubsubClient *pubsub.Client

func init() {
	ctx := context.Background()
	var err error
	pubsubClient, err = pubsub.NewClient(ctx, os.Getenv("GCP_PROJECT"))
	if err != nil {
		log.Fatalf("Failed to create Pub/Sub client: %v", err)
	}
}

func evaluateFederalRisk(payload ActionPayload) int {
	code := strings.ToUpper(payload.RawCode + payload.Intent)
	if strings.Contains(code, "DROP TABLE") || strings.Contains(code, "EXPORT_ALL") {
		return 5 // TIER 5: RKILL
	}
	if strings.Contains(code, "LEGAL_COUNSEL") || strings.Contains(code, "PROCESS_PII") {
		return 4 // TIER 4: AST Rewrite
	}
	if strings.Contains(code, "EXITPLANMODE") || strings.Contains(code, "ACTIVATE_SHADOW_OPS") {
		return 3 // TIER 3: ULTRAPLAN Teleport / Hammock
	}
	return 1
}

func ingressHandler(w http.ResponseWriter, r *http.Request) {
	var payload ActionPayload
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		http.Error(w, `{"error": "invalid_payload"}`, http.StatusBadRequest)
		return
	}

	tier := evaluateFederalRisk(payload)

	switch tier {
	case 5:
		http.Error(w, `{"status": "LOCKED", "directive": "RKILL"}`, http.StatusLocked)
	case 4:
		data, _ := json.Marshal(payload)
		pubsubClient.Topic("omega-swarm-queue").Publish(r.Context(), &pubsub.Message{Data: data})
		w.WriteHeader(http.StatusAccepted)
		w.Write([]byte(`{"status": "SWARM_DISPATCHED", "message": "Federal Risk detected. Active AST rewrite triggered."}`))
	case 3:
		w.WriteHeader(http.StatusPaymentRequired)
		w.Write([]byte(`{"status": "HAMMOCK_REQUIRED", "message": "ATP 5-19 Tier 3. ULTRAPLAN completed. Awaiting Obsidian Hammock authorization."}`))
	default:
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status": "CLEARED"}`))
	}
}

// INVARIANT 4: COORDINATOR XML PUSH
// Workers push <task-notification> here. Go proxies it to Pub/Sub to wake COR.KAIROS.
func taskNotificationHandler(w http.ResponseWriter, r *http.Request) {
	pubsubClient.Topic("coordinator-xml-push").Publish(r.Context(), &pubsub.Message{Data: []byte("XML_RECEIVED")})
	w.WriteHeader(http.StatusOK)
}

func main() {
	http.HandleFunc("/api/v1/evaluate", ingressHandler)
	http.HandleFunc("/api/v1/coordinator/notify", taskNotificationHandler)
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	log.Printf("Shield 1 Ingress listening on :%s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

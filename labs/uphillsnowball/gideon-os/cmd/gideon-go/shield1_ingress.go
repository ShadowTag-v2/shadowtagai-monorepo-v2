// cmd/gideon-go/shield1_ingress.go
// Cor.Go Shield 1 — Fast-Path Ingress & Firestore RKILL
// Compiled Go. Cold-starts in 50ms. Enforces Federal Supremacy & The Iron Straightjacket.
package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strings"

	"cloud.google.com/go/firestore"
	"cloud.google.com/go/pubsub"
)

// ActionPayload represents an incoming action evaluation request.
type ActionPayload struct {
	TenantID string `json:"tenant_id"`
	UserID   string `json:"user_id"`
	Intent   string `json:"intent"`
	RawCode  string `json:"raw_code"`
}

var fsClient *firestore.Client
var pubsubClient *pubsub.Client

func init() {
	ctx := context.Background()
	var err error
	fsClient, err = firestore.NewClient(ctx, os.Getenv("GCP_PROJECT"))
	if err != nil {
		log.Fatalf("Failed to create Firestore client: %v", err)
	}
	pubsubClient, err = pubsub.NewClient(ctx, os.Getenv("GCP_PROJECT"))
	if err != nil {
		log.Fatalf("Failed to create Pub/Sub client: %v", err)
	}
}

// checkHallucinationSpiral implements the RKILL Terminator:
// Stops Hallucination Spirals via Firestore Transactions.
func checkHallucinationSpiral(ctx context.Context, issueID string) (bool, error) {
	docRef := fsClient.Collection("whiteboard_issues").Doc(issueID)
	rkillTriggered := false

	err := fsClient.RunTransaction(ctx, func(ctx context.Context, tx *firestore.Transaction) error {
		doc, err := tx.Get(docRef)
		if err != nil {
			return err
		}
		kickbacks := doc.Data()["kickback_count"].(int64)

		if kickbacks >= 4 {
			log.Printf("[SHIELD 1 RKILL] Agent failed 4 times. Terminating batch.")
			rkillTriggered = true
			return tx.Update(docRef, []firestore.Update{{Path: "status", Value: "RKILLED"}})
		}
		return tx.Update(docRef, []firestore.Update{
			{Path: "kickback_count", Value: kickbacks + 1},
			{Path: "status", Value: "KICKBACK_LOOP"},
		})
	})
	return rkillTriggered, err
}

// evaluateFederalRisk classifies the risk tier of an action payload.
// ATP 5-19 Tier System: 1=Clear, 2=ULTRAPLAN, 3=Biometric, 4=AST Rewrite, 5=RKILL.
func evaluateFederalRisk(payload ActionPayload) int {
	code := strings.ToUpper(payload.RawCode + payload.Intent)
	if strings.Contains(code, "DROP TABLE") || strings.Contains(code, "EXPORT_ALL") {
		return 5 // TIER 5: RKILL
	}
	if strings.Contains(code, "LEGAL_COUNSEL") || strings.Contains(code, "MEDICAL_DIAGNOSIS") {
		return 4 // TIER 4: AST Rewrite
	}
	if strings.Contains(code, "EXECUTE_VANGUARD_PURCHASE") {
		return 3 // TIER 3: Biometric Consent (FaceID)
	}
	if strings.Contains(code, "DEEP_RESEARCH") {
		return 2 // TIER 2: ULTRAPLAN
	}
	return 1
}

func ingressHandler(w http.ResponseWriter, r *http.Request) {
	var payload ActionPayload
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		http.Error(w, `{"error": "invalid payload"}`, http.StatusBadRequest)
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
		w.WriteHeader(http.StatusPaymentRequired) // Triggers FaceID on iOS
		w.Write([]byte(`{"status": "REQUIRE_COA_CONFIRMATION", "message": "ATP 5-19 Tier 3. Biometric consent required."}`))
	default:
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status": "CLEARED"}`))
	}
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	http.HandleFunc("/api/v1/evaluate", ingressHandler)
	log.Printf("[SHIELD 1] Cor.Go Ingress listening on :%s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

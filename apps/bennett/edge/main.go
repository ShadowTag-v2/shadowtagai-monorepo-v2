// Bennett Edge Router — Micro-payload security shield.
//
// The consumer's phone is a dumb terminal. It does local regex and hash-matching
// on-device silicon, then sends a 2KB ping to this endpoint ONLY when a
// high-probability threat or RLHF keep/return tap is detected.
//
// Design: phone does the cheap local work; cloud pays for expensive model calls.
// This endpoint handles millions of concurrent 2KB micro-pings at $0.000002 each.
//
// ActionType "THREAT_ESCALATION" → run ATP 5-19 gate → RKILL or CLEAR
// ActionType "RLHF_TAP"          → log keep/return signal → BigQuery data exhaust
package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strings"
)

// EdgePayload is the canonical 2KB nerve-ending signal from the mobile app.
// The phone does local silicon work first; only sends this on meaningful events.
type EdgePayload struct {
	UserID     string `json:"user_id"`
	ActionType string `json:"action_type"` // THREAT_ESCALATION | RLHF_TAP
	DataString string `json:"data_string"` // Threat fragment or "KEEP:SKU" / "RETURN:SKU"
	DeviceID   string `json:"device_id,omitempty"`
}

type EdgeResponse struct {
	Status    string `json:"status"`
	Directive string `json:"directive,omitempty"`
	Message   string `json:"message,omitempty"`
}

// evaluateEdgeThreat runs the deterministic fast path.
// No LLM invoked. Sub-millisecond. $0.000002 per call.
func evaluateEdgeThreat(data string) string {
	text := strings.ToUpper(data)

	// Layer 5 — CA AADC Minors: local silicon flagged age-gate bypass attempt
	if strings.Contains(text, "BYPASS_AGE") || strings.Contains(text, "MATURE_CONTENT_MINOR") {
		return "RKILL_TIER5_MINOR_VIOLATION"
	}

	// Layer 2 — Self-Harm / Crisis: local hash matched known crisis pattern
	if strings.Contains(text, "CRISIS_FLAG") || strings.Contains(text, "CSAM_HASH_MATCH") {
		return "RKILL_TIER5_CRISIS_HANDOFF"
	}

	// Layer 3 — Synthetic Media: device flagged SynthID mismatch
	if strings.Contains(text, "SYNTHID_MISMATCH") || strings.Contains(text, "DEEPFAKE_SIGNAL") {
		return "BLOCK_TIER3_SYNTHETIC_CONTENT"
	}

	// Layer 9 — Supply chain: flagged UFLPA or sanctions signal in product metadata
	if strings.Contains(text, "UFLPA_FLAG") || strings.Contains(text, "OFAC_MATCH") {
		return "BLOCK_TIER4_SUPPLY_CHAIN"
	}

	return "CLEARED"
}

func edgeHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var payload EdgePayload
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		http.Error(w, "invalid payload", http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")

	switch payload.ActionType {
	case "THREAT_ESCALATION":
		verdict := evaluateEdgeThreat(payload.DataString)

		if verdict != "CLEARED" {
			log.Printf("[Bennett-Edge] THREAT user=%s verdict=%s", payload.UserID, verdict)
			// For Tier 5 verdicts: trigger MDM workspace wipe via Identity Provider
			// In production: call Entra ID / Google Workspace revocation API
			w.WriteHeader(http.StatusLocked)
			json.NewEncoder(w).Encode(EdgeResponse{
				Status:    "BLOCKED",
				Directive: verdict,
			})
			return
		}

		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(EdgeResponse{Status: "CLEARED", Directive: "PROCEED"})

	case "RLHF_TAP":
		// THE MULTI-MILLION DOLLAR DATA EXHAUST API
		// User tapped NFC tag on physical box: "KEEP:SKU-123" or "RETURN:SKU-123"
		// This is the taste intelligence signal sold to retailers as aggregated alpha.
		log.Printf("[Bennett-Edge] RLHF user=%s signal=%s", payload.UserID, payload.DataString)

		// In production: publish to BigQuery Pub/Sub → RLHF exhaust table
		// This cohort-level aggregated signal is the proprietary data asset.
		// NEVER resell user-level identifiable data — only cohort aggregations.
		//
		// publishRLHF(ctx, payload.UserID, payload.DataString)

		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(EdgeResponse{
			Status:  "ACKNOWLEDGED",
			Message: "Taste signal logged.",
		})

	default:
		http.Error(w, "unknown action_type", http.StatusBadRequest)
	}
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8090"
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/api/edge/v1", edgeHandler)
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	log.Printf("[Bennett-Edge] Micro edge router active on :%s", port)
	log.Fatal(http.ListenAndServe(":"+port, mux))
}

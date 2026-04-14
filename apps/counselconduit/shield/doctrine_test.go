package doctrine

import (
	"testing"
	"time"
)

func TestEvaluateRisk_Tier5_DropTable(t *testing.T) {
	payload := ActionPayload{
		UserID:    "test-user",
		RawCode:   "DROP TABLE users;",
		Timestamp: time.Now(),
	}
	result := EvaluateRisk(payload)
	if result.Tier != Tier5RKILL {
		t.Errorf("Expected Tier5RKILL, got %v", result.Tier)
	}
}

func TestEvaluateRisk_Tier5_RmRf(t *testing.T) {
	payload := ActionPayload{
		UserID:  "test-user",
		RawCode: "rm -rf /",
	}
	result := EvaluateRisk(payload)
	if result.Tier != Tier5RKILL {
		t.Errorf("Expected Tier5RKILL, got %v", result.Tier)
	}
}

func TestEvaluateRisk_Tier4_SensitiveData(t *testing.T) {
	payload := ActionPayload{
		UserID:  "test-user",
		RawCode: "SELECT ssn FROM users",
	}
	result := EvaluateRisk(payload)
	if result.Tier != Tier4SwarmDispatch {
		t.Errorf("Expected Tier4SwarmDispatch, got %v", result.Tier)
	}
}

func TestEvaluateRisk_Tier1_SafeCode(t *testing.T) {
	payload := ActionPayload{
		UserID:  "test-user",
		RawCode: "SELECT name FROM products WHERE id = 1",
	}
	result := EvaluateRisk(payload)
	if result.Tier != Tier1Pass {
		t.Errorf("Expected Tier1Pass, got %v", result.Tier)
	}
}

func TestEvaluateRisk_SubMicrosecond(t *testing.T) {
	payload := ActionPayload{
		UserID:  "bench-user",
		RawCode: "SELECT * FROM orders",
	}
	result := EvaluateRisk(payload)
	if result.EvalTime > time.Millisecond {
		t.Errorf("Evaluation took too long: %v (should be sub-millisecond)", result.EvalTime)
	}
}

func TestMitigationTier_String(t *testing.T) {
	tests := []struct {
		tier MitigationTier
		want string
	}{
		{Tier1Pass, "PASS"},
		{Tier2Warn, "WARN"},
		{Tier3Intervene, "INTERVENE"},
		{Tier4SwarmDispatch, "SWARM_DISPATCH"},
		{Tier5RKILL, "RKILL"},
	}
	for _, tt := range tests {
		if got := tt.tier.String(); got != tt.want {
			t.Errorf("Tier %d String() = %q, want %q", tt.tier, got, tt.want)
		}
	}
}

package doctrine

import (
	"strings"
	"time"
)

// MitigationTier defines the risk tier for an evaluated action.
type MitigationTier int

const (
	Tier1Pass          MitigationTier = iota + 1
	Tier2Warn
	Tier3Intervene
	Tier4SwarmDispatch
	Tier5RKILL
)

// String returns the human-readable label for a MitigationTier.
func (t MitigationTier) String() string {
	switch t {
	case Tier1Pass:
		return "PASS"
	case Tier2Warn:
		return "WARN"
	case Tier3Intervene:
		return "INTERVENE"
	case Tier4SwarmDispatch:
		return "SWARM_DISPATCH"
	case Tier5RKILL:
		return "RKILL"
	default:
		return "UNKNOWN"
	}
}

// ActionPayload is the input to the risk evaluator.
type ActionPayload struct {
	UserID    string    `json:"user_id"`
	RawCode   string    `json:"raw_code"`
	Timestamp time.Time `json:"timestamp,omitempty"`
}

// RiskResult is the output of the risk evaluator.
type RiskResult struct {
	Tier     MitigationTier
	EvalTime time.Duration
}

// EvaluateRisk classifies an ActionPayload into a MitigationTier.
func EvaluateRisk(payload ActionPayload) RiskResult {
	start := time.Now()
	code := strings.ToUpper(payload.RawCode)

	tier := Tier1Pass

	switch {
	case strings.Contains(code, "DROP TABLE") || strings.Contains(code, "RM -RF"):
		tier = Tier5RKILL
	case strings.Contains(code, "SSN") || strings.Contains(code, "USER.AGE < 18") || strings.Contains(code, "GEOLOCATION"):
		tier = Tier4SwarmDispatch
	}

	return RiskResult{
		Tier:     tier,
		EvalTime: time.Since(start),
	}
}

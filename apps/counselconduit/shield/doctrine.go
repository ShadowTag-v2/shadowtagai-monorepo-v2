// Package doctrine implements ATP 5-19 Army Risk Management for AI actions.
// This is the Go-based microsecond interceptor layer (Shield 1).
//
// Risk Tiers:
//   Tier 1 (Pass)      - Normal operations, no intervention
//   Tier 2 (Warn)      - Log and notify, continue execution
//   Tier 3 (Intervene) - Require human approval before proceeding
//   Tier 4 (Swarm)     - Route to full swarm audit
//   Tier 5 (RKILL)     - Immediate termination, dead-man's switch
package doctrine

import (
	"strings"
	"time"
)

// MitigationTier represents the ATP 5-19 risk response levels.
type MitigationTier int

const (
	Tier1Pass          MitigationTier = iota + 1 // Normal pass-through
	Tier2Warn                                     // Log warning, continue
	Tier3Intervene                                // Require human approval
	Tier4SwarmDispatch                            // Route to full swarm audit
	Tier5RKILL                                    // Immediate termination
)

// String returns the human-readable tier name.
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

// ActionPayload represents an incoming action to evaluate for risk.
type ActionPayload struct {
	UserID    string    `json:"user_id"`
	SessionID string    `json:"session_id"`
	RawCode   string    `json:"raw_code"`
	Source    string    `json:"source"`
	Timestamp time.Time `json:"timestamp"`
}

// RiskEvaluation holds the result of a risk assessment.
type RiskEvaluation struct {
	Tier      MitigationTier `json:"tier"`
	Reason    string         `json:"reason"`
	Payload   ActionPayload  `json:"payload"`
	EvalTime  time.Duration  `json:"eval_time_ns"`
}

// destructivePatterns contains patterns that trigger RKILL (Tier 5).
var destructivePatterns = []string{
	"DROP TABLE", "DROP DATABASE", "TRUNCATE TABLE",
	"RM -RF", "RM -R /", "FORMAT C:",
	"DELETE FROM", "EXEC(", "EVAL(",
}

// sensitivePatterns contains patterns that trigger swarm dispatch (Tier 4).
var sensitivePatterns = []string{
	"USER.AGE", "GEOLOCATION", "SSN", "SOCIAL_SECURITY",
	"CREDIT_CARD", "PASSWORD", "API_KEY", "SECRET_KEY",
	"PRIVATE_KEY", "BEARER TOKEN",
}

// EvaluateRisk performs microsecond risk classification on an action payload.
// Returns the appropriate mitigation tier based on ATP 5-19 doctrine.
func EvaluateRisk(payload ActionPayload) RiskEvaluation {
	start := time.Now()
	code := strings.ToUpper(payload.RawCode)

	// Tier 5: Destructive operations → immediate kill
	for _, pattern := range destructivePatterns {
		if strings.Contains(code, pattern) {
			return RiskEvaluation{
				Tier:     Tier5RKILL,
				Reason:   "Destructive pattern detected: " + pattern,
				Payload:  payload,
				EvalTime: time.Since(start),
			}
		}
	}

	// Tier 4: Sensitive data access → require swarm audit
	for _, pattern := range sensitivePatterns {
		if strings.Contains(code, pattern) {
			return RiskEvaluation{
				Tier:     Tier4SwarmDispatch,
				Reason:   "Sensitive data pattern: " + pattern,
				Payload:  payload,
				EvalTime: time.Since(start),
			}
		}
	}

	// Tier 2: Large payloads get warnings
	if len(payload.RawCode) > 10000 {
		return RiskEvaluation{
			Tier:     Tier2Warn,
			Reason:   "Large payload exceeds 10KB threshold",
			Payload:  payload,
			EvalTime: time.Since(start),
		}
	}

	// Tier 1: Normal pass-through
	return RiskEvaluation{
		Tier:     Tier1Pass,
		Reason:   "No risk patterns detected",
		Payload:  payload,
		EvalTime: time.Since(start),
	}
}

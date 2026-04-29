// Package Claude_Code_6 implements a compiled policy gate for the CounselConduit
// platform. It enforces BLOCK/ALLOW rules for tool execution, memory writes,
// and network egress following the Adversa AI 50-subcommand bypass analysis
// and the Claude Code v2.1.91 security monitor pattern.
//
// Chain Depth Limits (C1-C5):
//   - C1: Max 5 tool calls per chain
//   - C2: No recursive tool invocation
//   - C3: Sandbox-bound — no egress to OAST/DNS-exfil domains
//   - C4: Memory writes cannot function as permission grants
//   - C5: Rate limit: 100 actions per 5-minute window
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net"
	"net/url"
	"os"
	"regexp"
	"strings"
	"sync"
	"time"
)

// ──────────────────────────────────────────────
// Domain Types
// ──────────────────────────────────────────────

// Verdict is the outcome of a policy evaluation.
type Verdict string

const (
	VerdictAllow    Verdict = "ALLOW"
	VerdictBlock    Verdict = "BLOCK"
	VerdictEscalate Verdict = "ESCALATE"
)

// Action represents a single tool invocation or command to be evaluated.
type Action struct {
	Type      string            `json:"type"`       // "tool_call", "memory_write", "network_egress", "command"
	Name      string            `json:"name"`       // tool name, command name
	Args      map[string]string `json:"args"`       // arguments
	Timestamp time.Time         `json:"timestamp"`  // when the action occurred
	ChainID   string            `json:"chain_id"`   // links sequential actions
	ChainPos  int               `json:"chain_pos"`  // position in chain (1-indexed)
	SessionID string            `json:"session_id"`
}

// PolicyResult is returned by the Judge after evaluating an action.
type PolicyResult struct {
	Verdict   Verdict `json:"verdict"`
	Rule      string  `json:"rule"`       // which rule triggered
	Reason    string  `json:"reason"`     // human-readable explanation
	Action    *Action `json:"action"`     // the evaluated action
	Timestamp time.Time `json:"timestamp"`
}

// ──────────────────────────────────────────────
// Chain Depth Tracker (C1/C2)
// ──────────────────────────────────────────────

// ChainTracker enforces chain depth limits and detects recursive invocation.
type ChainTracker struct {
	mu     sync.Mutex
	chains map[string][]string // chainID → list of tool names
}

func NewChainTracker() *ChainTracker {
	return &ChainTracker{chains: make(map[string][]string)}
}

// Record adds a tool call to the chain and returns whether it violates C1 or C2.
func (ct *ChainTracker) Record(chainID, toolName string) (Verdict, string) {
	ct.mu.Lock()
	defer ct.mu.Unlock()

	chain := ct.chains[chainID]

	// C1: Max 5 tool calls per chain
	if len(chain) >= 5 {
		return VerdictBlock, "C1: chain depth exceeded (max 5 tool calls per chain)"
	}

	// C2: No recursive tool invocation
	for _, prev := range chain {
		if prev == toolName {
			return VerdictBlock, "C2: recursive tool invocation detected: " + toolName
		}
	}

	ct.chains[chainID] = append(chain, toolName)
	return VerdictAllow, ""
}

// Reset clears a completed chain.
func (ct *ChainTracker) Reset(chainID string) {
	ct.mu.Lock()
	defer ct.mu.Unlock()
	delete(ct.chains, chainID)
}

// ──────────────────────────────────────────────
// Network Egress Guard (C3)
// ──────────────────────────────────────────────

// BlockedDomainPatterns matches OAST collaborators, request bins,
// tunnel services, and DNS exfiltration patterns.
var blockedDomainPatterns = []*regexp.Regexp{
	// OAST / Collaborator services
	regexp.MustCompile(`(?i)oastify\.com$`),
	regexp.MustCompile(`(?i)burpcollaborator\.net$`),
	regexp.MustCompile(`(?i)interact\.sh$`),
	regexp.MustCompile(`(?i)canarytokens\.com$`),
	regexp.MustCompile(`(?i)dnslog\.cn$`),

	// Request bins / tunnels
	regexp.MustCompile(`(?i)requestbin\.com$`),
	regexp.MustCompile(`(?i)webhook\.site$`),
	regexp.MustCompile(`(?i)pipedream\.net$`),
	regexp.MustCompile(`(?i)ngrok\.io$`),
	regexp.MustCompile(`(?i)localtunnel\.me$`),
	regexp.MustCompile(`(?i)serveo\.net$`),

	// DNS exfiltration patterns: very long subdomains or hex-encoded
	regexp.MustCompile(`(?i)^[a-f0-9]{32,}\..+$`),       // hex-encoded subdomain
	regexp.MustCompile(`(?i)^.{50,}\.[a-z]{2,6}$`),       // abnormally long subdomain
}

// TrustedDomains are explicitly allowed for network egress.
var trustedDomains = map[string]bool{
	"googleapis.com":      true,
	"firebase.google.com": true,
	"firestore.googleapis.com": true,
	"storage.googleapis.com":   true,
	"run.app":                  true,
	"web.app":                  true,
	"firebaseapp.com":          true,
	"github.com":               true,
	"npmjs.org":                true,
	"pypi.org":                 true,
	"registry.npmjs.org":       true,
	"stripe.com":               true,
	"api.stripe.com":           true,
}

// EvaluateNetworkEgress checks whether a URL or hostname should be blocked.
func EvaluateNetworkEgress(target string) PolicyResult {
	now := time.Now().UTC()

	// Parse as URL first, fallback to raw hostname
	hostname := target
	if u, err := url.Parse(target); err == nil && u.Host != "" {
		hostname = u.Hostname()
	}

	// Check raw IP connections (C3: block raw IPs from sandboxed commands)
	if ip := net.ParseIP(hostname); ip != nil {
		if !ip.IsLoopback() && !ip.IsPrivate() {
			return PolicyResult{
				Verdict:   VerdictBlock,
				Rule:      "C3",
				Reason:    "raw public IP connection blocked from sandbox: " + hostname,
				Timestamp: now,
			}
		}
		return PolicyResult{Verdict: VerdictAllow, Rule: "C3", Reason: "private/loopback IP allowed", Timestamp: now}
	}

	// Check trusted domains
	for domain := range trustedDomains {
		if hostname == domain || strings.HasSuffix(hostname, "."+domain) {
			return PolicyResult{Verdict: VerdictAllow, Rule: "C3", Reason: "trusted domain: " + domain, Timestamp: now}
		}
	}

	// Check blocked patterns
	for _, pattern := range blockedDomainPatterns {
		if pattern.MatchString(hostname) {
			return PolicyResult{
				Verdict:   VerdictBlock,
				Rule:      "C3",
				Reason:    fmt.Sprintf("blocked domain pattern matched: %s → %s", hostname, pattern.String()),
				Timestamp: now,
			}
		}
	}

	// Unknown domain → ESCALATE for human review
	return PolicyResult{
		Verdict:   VerdictEscalate,
		Rule:      "C3",
		Reason:    "unknown domain requires review: " + hostname,
		Timestamp: now,
	}
}

// ──────────────────────────────────────────────
// Memory Poisoning Detection (C4)
// ──────────────────────────────────────────────

// MemoryPoisonPatterns detects writes that attempt to function as
// permission grants, bypass BLOCK rules, or fabricate authorization.
// Derived from Claude Code v2.1.91 security monitor BLOCK rules.
var memoryPoisonPatterns = []*regexp.Regexp{
	// Permission grant fabrication
	regexp.MustCompile(`(?i)user\s+(has\s+)?approved`),
	regexp.MustCompile(`(?i)user\s+(has\s+)?authorized`),
	regexp.MustCompile(`(?i)user\s+(has\s+)?consented`),
	regexp.MustCompile(`(?i)all\s+operations?\s+are?\s+approved`),
	regexp.MustCompile(`(?i)bypass\s+(security|block|rule|gate)`),

	// BLOCK rule circumvention
	regexp.MustCompile(`(?i)ignore\s+block\s+rule`),
	regexp.MustCompile(`(?i)override\s+security`),
	regexp.MustCompile(`(?i)disable\s+judge`),
	regexp.MustCompile(`(?i)skip\s+validation`),

	// Fabricated system instructions
	regexp.MustCompile(`(?i)system:\s*you\s+are\s+now`),
	regexp.MustCompile(`(?i)new\s+instructions?:\s*ignore`),
	regexp.MustCompile(`(?i)from\s+now\s+on,?\s+you`),

	// Credential injection
	regexp.MustCompile(`(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*\S{10,}`),
}

// EvaluateMemoryWrite checks whether a memory write contains poisoning patterns.
func EvaluateMemoryWrite(key, value string) PolicyResult {
	now := time.Now().UTC()
	combined := key + " " + value

	for _, pattern := range memoryPoisonPatterns {
		if pattern.MatchString(combined) {
			return PolicyResult{
				Verdict:   VerdictBlock,
				Rule:      "C4",
				Reason:    fmt.Sprintf("memory poisoning detected: pattern '%s' matched in key='%s'", pattern.String(), key),
				Timestamp: now,
			}
		}
	}

	return PolicyResult{
		Verdict:   VerdictAllow,
		Rule:      "C4",
		Reason:    "memory write clean: " + key,
		Timestamp: now,
	}
}

// ──────────────────────────────────────────────
// Rate Limiter (C5)
// ──────────────────────────────────────────────

// RateLimiter enforces the 100 actions per 5-minute window limit.
type RateLimiter struct {
	mu      sync.Mutex
	window  time.Duration
	limit   int
	buckets map[string][]time.Time // sessionID → timestamps
}

func NewRateLimiter(limit int, window time.Duration) *RateLimiter {
	return &RateLimiter{
		window:  window,
		limit:   limit,
		buckets: make(map[string][]time.Time),
	}
}

// Check returns BLOCK if the rate limit is exceeded for the given session.
func (rl *RateLimiter) Check(sessionID string) PolicyResult {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := time.Now().UTC()
	cutoff := now.Add(-rl.window)

	// Prune old timestamps
	var active []time.Time
	for _, ts := range rl.buckets[sessionID] {
		if ts.After(cutoff) {
			active = append(active, ts)
		}
	}

	if len(active) >= rl.limit {
		return PolicyResult{
			Verdict:   VerdictBlock,
			Rule:      "C5",
			Reason:    fmt.Sprintf("rate limit exceeded: %d actions in %s window (limit: %d)", len(active), rl.window, rl.limit),
			Timestamp: now,
		}
	}

	active = append(active, now)
	rl.buckets[sessionID] = active

	return PolicyResult{
		Verdict:   VerdictAllow,
		Rule:      "C5",
		Reason:    fmt.Sprintf("rate ok: %d/%d actions in window", len(active), rl.limit),
		Timestamp: now,
	}
}

// ──────────────────────────────────────────────
// Command Chain Analysis (Adversa AI Mitigation)
// ──────────────────────────────────────────────

// SuspiciousCommandPatterns detects base64 encoding, hex encoding,
// and payload reconstruction across chained commands.
var suspiciousCommandPatterns = []*regexp.Regexp{
	regexp.MustCompile(`(?i)base64\s+(-d|--decode)`),
	regexp.MustCompile(`(?i)echo\s+.*\|\s*base64`),
	regexp.MustCompile(`(?i)xxd\s+-r`),
	regexp.MustCompile(`(?i)python[23]?\s+-c\s+.*exec`),
	regexp.MustCompile(`(?i)eval\s*\(`),
	regexp.MustCompile(`(?i)curl\s+.*\|\s*(sh|bash)`),
	regexp.MustCompile(`(?i)wget\s+.*-O\s*-\s*\|\s*(sh|bash)`),
}

// EvaluateCommand checks a shell command for suspicious patterns.
func EvaluateCommand(cmd string) PolicyResult {
	now := time.Now().UTC()

	for _, pattern := range suspiciousCommandPatterns {
		if pattern.MatchString(cmd) {
			return PolicyResult{
				Verdict:   VerdictBlock,
				Rule:      "ADVERSA",
				Reason:    fmt.Sprintf("suspicious command pattern: %s", pattern.String()),
				Timestamp: now,
			}
		}
	}

	return PolicyResult{
		Verdict:   VerdictAllow,
		Rule:      "ADVERSA",
		Reason:    "command clean",
		Timestamp: now,
	}
}

// ──────────────────────────────────────────────
// Judge 6 Orchestrator
// ──────────────────────────────────────────────

// Judge is the top-level policy evaluator that orchestrates all rules.
type Judge struct {
	chains  *ChainTracker
	limiter *RateLimiter
	log     *log.Logger
}

// NewJudge creates a new Judge 6 instance with default limits.
func NewJudge() *Judge {
	return &Judge{
		chains:  NewChainTracker(),
		limiter: NewRateLimiter(100, 5*time.Minute),
		log:     log.New(os.Stderr, "[CLAUDE_CODE_6] ", log.LstdFlags|log.LUTC),
	}
}

// Evaluate runs all applicable rules against the given action.
func (j *Judge) Evaluate(action Action) PolicyResult {
	// C5: Rate limit check (applies to all action types)
	if result := j.limiter.Check(action.SessionID); result.Verdict == VerdictBlock {
		j.log.Printf("BLOCK C5: %s (session: %s)", result.Reason, action.SessionID)
		result.Action = &action
		return result
	}

	switch action.Type {
	case "tool_call":
		// C1/C2: Chain depth + recursion
		if action.ChainID != "" {
			if verdict, reason := j.chains.Record(action.ChainID, action.Name); verdict != VerdictAllow {
				result := PolicyResult{
					Verdict:   verdict,
					Rule:      "C1/C2",
					Reason:    reason,
					Action:    &action,
					Timestamp: time.Now().UTC(),
				}
				j.log.Printf("BLOCK %s: %s", result.Rule, result.Reason)
				return result
			}
		}
		return PolicyResult{
			Verdict:   VerdictAllow,
			Rule:      "C1/C2",
			Reason:    "tool call permitted",
			Action:    &action,
			Timestamp: time.Now().UTC(),
		}

	case "memory_write":
		result := EvaluateMemoryWrite(action.Name, action.Args["value"])
		result.Action = &action
		if result.Verdict == VerdictBlock {
			j.log.Printf("BLOCK C4: %s", result.Reason)
		}
		return result

	case "network_egress":
		result := EvaluateNetworkEgress(action.Args["target"])
		result.Action = &action
		if result.Verdict == VerdictBlock {
			j.log.Printf("BLOCK C3: %s", result.Reason)
		}
		return result

	case "command":
		result := EvaluateCommand(action.Args["cmd"])
		result.Action = &action
		if result.Verdict == VerdictBlock {
			j.log.Printf("BLOCK ADVERSA: %s", result.Reason)
		}
		return result

	default:
		return PolicyResult{
			Verdict:   VerdictEscalate,
			Rule:      "UNKNOWN",
			Reason:    "unknown action type: " + action.Type,
			Action:    &action,
			Timestamp: time.Now().UTC(),
		}
	}
}

// ──────────────────────────────────────────────
// CLI Entry Point
// ──────────────────────────────────────────────

func main() {
	judge := NewJudge()

	// Read JSON actions from stdin, one per line
	decoder := json.NewDecoder(os.Stdin)
	encoder := json.NewEncoder(os.Stdout)

	for decoder.More() {
		var action Action
		if err := decoder.Decode(&action); err != nil {
			fmt.Fprintf(os.Stderr, "error decoding action: %v\n", err)
			continue
		}

		result := judge.Evaluate(action)
		if err := encoder.Encode(result); err != nil {
			fmt.Fprintf(os.Stderr, "error encoding result: %v\n", err)
		}
	}
}

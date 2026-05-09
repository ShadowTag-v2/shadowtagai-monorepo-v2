/**
 * V23 Mailbox Policies — TypeScript companion to Python AgentMailbox
 * Defines policy catalog and risk-based agent selection for
 * multi-agent plan approval delegation.
 */

export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface AgentRole {
  model: string;
  veto_power: boolean;
  required_for: string[];
  auto_approve_threshold: number;
}

export interface VoteRecord {
  agent: string;
  vote: "approve" | "reject" | "abstain";
  confidence: number;
  reasoning: string;
  timestamp: number;
  latency_ms: number;
}

export interface PlanEnvelope {
  planId: string;
  riskLevel: RiskLevel;
  requiredAgents: string[];
  votes: VoteRecord[];
  status: "pending" | "approved" | "rejected" | "expired";
  createdAt: number;
  resolvedAt?: number;
}

const RISK_ESCALATION: Record<string, string[]> = {
  low: ["cost_analyst"],
  medium: ["cost_analyst", "architecture_board"],
  high: ["security_reviewer", "cost_analyst", "architecture_board"],
  critical: ["security_reviewer", "cost_analyst", "architecture_board"],
};

const CONSENSUS_THRESHOLD = 0.85;
const VOTE_TIMEOUT_MS = 30000;
const MAX_VOTE_LATENCY_MS = 150;

export function selectAgentsForRisk(riskLevel: RiskLevel): string[] {
  return RISK_ESCALATION[riskLevel] ?? RISK_ESCALATION["high"];
}

const VETO_AGENTS = new Set(["security_reviewer", "architecture_board"]);

export function hasVetoPower(agentName: string): boolean {
  return VETO_AGENTS.has(agentName);
}

export function resolveEnvelope(envelope: PlanEnvelope): PlanEnvelope["status"] {
  if (Date.now() - envelope.createdAt > VOTE_TIMEOUT_MS) return "expired";

  const votedAgents = new Set(envelope.votes.map((v) => v.agent));
  if (!envelope.requiredAgents.every((a) => votedAgents.has(a))) return "pending";

  for (const vote of envelope.votes) {
    if (vote.vote === "reject" && hasVetoPower(vote.agent)) return "rejected";
  }

  const approvals = envelope.votes.filter((v) => v.vote === "approve").length;
  const total = envelope.votes.filter((v) => v.vote !== "abstain").length;
  return total > 0 && approvals / total >= CONSENSUS_THRESHOLD ? "approved" : "rejected";
}

export function createEnvelope(planId: string, riskLevel: RiskLevel): PlanEnvelope {
  return {
    planId, riskLevel,
    requiredAgents: selectAgentsForRisk(riskLevel),
    votes: [], status: "pending", createdAt: Date.now(),
  };
}

export function castVote(envelope: PlanEnvelope, vote: VoteRecord): boolean {
  if (envelope.votes.some((v) => v.agent === vote.agent)) return false;
  if (envelope.status !== "pending") return false;
  if (vote.latency_ms > MAX_VOTE_LATENCY_MS) { /* log but accept */ }
  envelope.votes.push(vote);
  envelope.status = resolveEnvelope(envelope);
  if (envelope.status !== "pending") envelope.resolvedAt = Date.now();
  return true;
}

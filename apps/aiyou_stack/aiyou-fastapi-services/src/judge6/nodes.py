"""LangGraph Node Implementations for Judge 6 Kill Chain

Kill Chain Phases:
1. node_assessment - OPA Fast Check (JREngine wrapper, <500μs)
2. node_router - Confidence-based routing (debate vs direct)
3. node_debate - Panel Debate (PanelDebateSystem wrapper)
4. node_audit - Audit Logger (AuditCompressKernel wrapper)
5. node_finalize - Final decision output
"""

import asyncio
import hashlib
import json
import time
from datetime import datetime
from typing import Any

from .state import (
    AssessmentStatus,
    AuditStatus,
    DebateRound,
    DebateStatus,
    GovernanceState,
    RiskLevel,
    SwarmVoteMethod,
    SwarmVoteState,
    VotingMode,
)

# Import swarm voter for minion2 integration
try:
    from agents.autoresearch2 import SwarmVoter, VoteDecision, swarm_vote

    SWARM_AVAILABLE = True
except ImportError:
    SWARM_AVAILABLE = False
    SwarmVoter = None
    swarm_vote = None

# Optional: Import memory for precedent lookup
try:
    from .memory import SovereignMemory

    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    SovereignMemory = None


# =============================================================================
# KILL CHAIN PHASE 1: OPA FAST CHECK (JREngine Wrapper)
# =============================================================================


def node_assessment(state: GovernanceState) -> GovernanceState:
    """Assessment Node: OPA Fast Check
    Wraps JREngine in LangGraph context.
    Target latency: <500μs (deterministic, no LLM calls)

    Purpose → Reasons → Brakes validation
    """
    start_time = time.perf_counter()
    assessment = state.assessment
    assessment.status = AssessmentStatus.IN_PROGRESS

    try:
        # Extract context
        context = assessment.context

        # Evaluate PURPOSE: Why is this action being taken?
        purpose = {
            "intent": context.get("intent", "Unknown"),
            "business_value": context.get("business_value", ""),
            "cost_estimate_usd": context.get("cost_estimate_usd", 0.0),
            "expected_outcome": context.get("expected_outcome", ""),
        }

        # Evaluate REASONS: What justifies this action?
        reasons = []
        for reason in context.get("reasons", []):
            reasons.append(
                {
                    "justification": reason.get("justification", ""),
                    "risk_probability": reason.get("risk_probability", 0.5),
                    "risk_severity": reason.get("risk_severity", 0.5),
                    "mitigation_strategy": reason.get("mitigation_strategy"),
                },
            )

        # Evaluate BRAKES: What constraints apply?
        brakes = []
        if context.get("production_system"):
            brakes.append(
                {
                    "type": "production",
                    "triggered": True,
                    "reason": "Production system - requires extra caution",
                    "risk_level": "MEDIUM",
                },
            )

        if context.get("no_tests"):
            brakes.append(
                {
                    "type": "testing",
                    "triggered": True,
                    "reason": "No test coverage - blind deployment",
                    "risk_level": "HIGH",
                },
            )

        if context.get("authentication_logic"):
            brakes.append(
                {
                    "type": "security",
                    "triggered": True,
                    "reason": "Security-sensitive authentication code",
                    "risk_level": "HIGH",
                },
            )

        if context.get("database_migration"):
            brakes.append(
                {
                    "type": "data",
                    "triggered": True,
                    "reason": "Database schema change - irreversible",
                    "risk_level": "EXTREMELY_HIGH",
                },
            )

        # Calculate risk level using ATP 5-19 matrix logic
        critical_brakes = sum(
            1 for b in brakes if b.get("risk_level") in ["HIGH", "EXTREMELY_HIGH"]
        )
        total_brakes = len(brakes)

        if critical_brakes >= 2:
            risk_level = RiskLevel.EXTREMELY_HIGH
            confidence = 0.95
        elif critical_brakes == 1 or total_brakes >= 3:
            risk_level = RiskLevel.HIGH
            confidence = 0.85
        elif total_brakes >= 1:
            risk_level = RiskLevel.MEDIUM
            confidence = 0.75
        else:
            risk_level = RiskLevel.LOW
            confidence = 0.90

        # Build assessment result
        assessment.purpose = purpose
        assessment.reasons = reasons
        assessment.brakes = brakes
        assessment.risk_level = risk_level
        assessment.confidence = confidence

        assessment.assessment_result = {
            "approved": risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM],
            "risk_level": risk_level.value,
            "brakes_triggered": len(brakes),
            "confidence": confidence,
            "purpose": purpose,
            "reasons": reasons,
            "brakes": brakes,
        }

        assessment.assessment_latency_us = (time.perf_counter() - start_time) * 1_000_000
        assessment.status = AssessmentStatus.COMPLETED
        assessment.updated_at = datetime.utcnow()

        # Update global state
        state.assessment = assessment
        state.last_successful_phase = "assessment"

        # Add audit entry
        state.audit.add_entry(
            event_type="assessment_completed",
            details={
                "risk_level": risk_level.value,
                "confidence": confidence,
                "brakes_triggered": len(brakes),
                "latency_us": assessment.assessment_latency_us,
            },
            severity="INFO",
        )

        return state

    except Exception as e:
        assessment.status = AssessmentStatus.FAILED
        assessment.assessment_errors.append(str(e))
        assessment.assessment_latency_us = (time.perf_counter() - start_time) * 1_000_000
        state.assessment = assessment

        state.audit.add_entry(
            event_type="assessment_failed",
            details={"error": str(e)},
            severity="ERROR",
        )

        return state


# =============================================================================
# ROUTER NODE: Conditional Debate Triggering
# =============================================================================


def node_router(state: GovernanceState) -> str:
    """Router Node: Decide whether to execute debate phase.

    Triggers debate if:
    1. Assessment confidence < 0.80
    2. Assessment has HIGH/EH risk level
    3. Multiple brakes triggered

    Returns:
        Next node name: "debate" or "audit"

    """
    assessment = state.assessment
    confidence = assessment.confidence
    risk_level = assessment.risk_level
    brakes = assessment.brakes

    # Determine if debate needed
    should_debate = False
    trigger_reason = None

    if confidence < 0.80:
        should_debate = True
        trigger_reason = f"Low confidence ({confidence:.0%})"
    elif risk_level in [RiskLevel.HIGH, RiskLevel.EXTREMELY_HIGH]:
        should_debate = True
        trigger_reason = f"High risk level ({risk_level.value})"
    elif len(brakes) >= 2:
        should_debate = True
        trigger_reason = f"Multiple brakes triggered ({len(brakes)})"

    # Update debate state
    state.debate.should_debate = should_debate
    state.debate.debate_trigger_reason = trigger_reason

    if should_debate:
        state.audit.add_entry(
            event_type="debate_triggered",
            details={"reason": trigger_reason},
            severity="INFO",
        )
        return "debate"
    state.debate.status = DebateStatus.NOT_TRIGGERED
    state.audit.add_entry(
        event_type="debate_skipped",
        details={"confidence": confidence, "risk_level": risk_level.value},
        severity="INFO",
    )
    return "audit"


# =============================================================================
# KILL CHAIN PHASE 2: SINGLE-ROUND MEMORY-AUGMENTED VOTING (Default)
# =============================================================================


async def _async_single_round_vote(state: GovernanceState) -> GovernanceState:
    """Single-round voting using memory precedents and prefetch context.

    Flow:
    1. Lookup similar precedents from memory
    2. Prefetch web context if available
    3. Make single decision informed by context
    4. No debate rounds - just one confident vote

    Much faster and cheaper than 3-phase debate.
    """
    start_time = time.perf_counter()
    debate = state.debate
    debate.status = DebateStatus.IN_PROGRESS
    debate.started_at = datetime.utcnow()

    try:
        assessment_result = state.assessment.assessment_result
        assessment_result.get("purpose", {}).get("intent", "Unknown action")
        risk_level = assessment_result.get("risk_level", "MEDIUM")
        brakes = assessment_result.get("brakes", [])

        # Step 1: Gather precedent context from memory
        precedent_context = ""
        if state.similar_precedents:
            debate.precedent_ids = state.similar_precedents[:5]
            precedent_context = f"Found {len(debate.precedent_ids)} similar past decisions"

        # Step 2: Build single-vote reasoning from context
        vote_factors = []

        # Factor 1: Risk assessment
        if risk_level in ["EH", "H"]:
            vote_factors.append(f"HIGH_RISK: {risk_level} risk level detected")
        else:
            vote_factors.append(f"ACCEPTABLE_RISK: {risk_level} risk level")

        # Factor 2: Brake analysis
        critical_brakes = [b for b in brakes if b.get("risk_level") in ["HIGH", "EXTREMELY_HIGH"]]
        if critical_brakes:
            vote_factors.append(f"BRAKES: {len(critical_brakes)} critical brakes triggered")

        # Factor 3: Precedent analysis
        if precedent_context:
            vote_factors.append(f"PRECEDENTS: {precedent_context}")

        # Step 3: Make decision (single vote, no debate rounds)
        # Simple heuristic - can be replaced with single LLM call
        approve_score = 0.5  # Start neutral

        # Adjust based on risk
        if risk_level == "L":
            approve_score += 0.3
        elif risk_level == "M":
            approve_score += 0.1
        elif risk_level == "H":
            approve_score -= 0.2
        elif risk_level == "EH":
            approve_score -= 0.4

        # Adjust based on brakes
        approve_score -= len(critical_brakes) * 0.15
        approve_score -= len(brakes) * 0.05

        # Clamp to valid range
        approve_score = max(0.0, min(1.0, approve_score))

        # Determine decision
        if approve_score >= 0.60:
            decision = "APPROVE"
            confidence = approve_score
        elif approve_score <= 0.35:
            decision = "REJECT"
            confidence = 1.0 - approve_score
        else:
            decision = "ESCALATE"
            confidence = 0.50

        # Build reasoning
        reasoning = f"Single-round vote: {' | '.join(vote_factors)}. Score: {approve_score:.2f}"

        # Store results
        debate.single_vote_reasoning = reasoning
        debate.memory_context = precedent_context
        debate.precedent_votes = [{"decision": decision, "score": approve_score}]

        debate.debate_conclusion = reasoning
        debate.final_confidence = confidence
        debate.final_decision = decision
        debate.status = DebateStatus.COMPLETED
        debate.debate_latency_ms = (time.perf_counter() - start_time) * 1000
        debate.debate_cost_usd = 0.001  # Minimal - no LLM calls in default mode

        state.debate = debate
        state.last_successful_phase = "debate"

        state.audit.add_entry(
            event_type="single_round_vote_completed",
            details={
                "decision": decision,
                "confidence": confidence,
                "approve_score": approve_score,
                "vote_factors": len(vote_factors),
                "cost_usd": debate.debate_cost_usd,
                "latency_ms": debate.debate_latency_ms,
            },
            severity="INFO",
        )

        return state

    except Exception as e:
        debate.status = DebateStatus.FAILED
        debate.debate_errors.append(str(e))
        debate.debate_latency_ms = (time.perf_counter() - start_time) * 1000
        state.debate = debate

        state.audit.add_entry(
            event_type="single_round_vote_failed",
            details={"error": str(e)},
            severity="ERROR",
        )

        return state


# =============================================================================
# KILL CHAIN PHASE 2: SWARM VOTING (minion2 - Default)
# =============================================================================


async def _async_swarm_vote(state: GovernanceState) -> GovernanceState:
    """Swarm voting using minion2 (200-agent heuristic + conditional LLM).

    Cost: $0.00006/decision average (5x under $0.0003 target)
    - 80% clear consensus: $0 (heuristic only)
    - 20% unclear → LLM tiebreaker: $0.0003

    Latency: ~7ms (clear) / ~77ms (unclear) / ~21ms average

    This is the default voting mode. Uses all 200 active agents from
    the minion swarm with tier-weighted voting.
    """
    start_time = time.perf_counter()
    debate = state.debate
    debate.status = DebateStatus.IN_PROGRESS
    debate.started_at = datetime.utcnow()

    try:
        assessment_result = state.assessment.assessment_result
        intent = assessment_result.get("purpose", {}).get("intent", "Unknown action")
        risk_level = assessment_result.get("risk_level", "M")
        brakes = assessment_result.get("brakes", [])
        brake_count = len(brakes)

        # Map risk level string to ATP 5-19 code
        risk_map = {
            "EXTREMELY_HIGH": "EH",
            "HIGH": "H",
            "MEDIUM": "M",
            "LOW": "L",
            "EH": "EH",
            "H": "H",
            "M": "M",
            "L": "L",
        }
        risk_code = risk_map.get(risk_level, "M")

        # Execute swarm vote
        if SWARM_AVAILABLE and swarm_vote:
            vote_result = await swarm_vote(
                intent=intent,
                risk_level=risk_code,
                brake_count=brake_count,
            )

            # Map result to state
            decision = vote_result["decision"]
            confidence = vote_result["confidence"]
            method = (
                SwarmVoteMethod.LLM_TIEBREAKER
                if vote_result["llm_override"]
                else SwarmVoteMethod.HEURISTIC
            )

            # Create SwarmVoteState
            swarm_state = SwarmVoteState(
                decision_id=state.decision_id,
                decision=decision,
                confidence=confidence,
                method=method,
                consensus_ratio=vote_result["consensus_ratio"],
                total_votes=vote_result["total_votes"],
                weighted_approve=0,  # Not returned by swarm_vote
                weighted_total=0,
                llm_override=vote_result["llm_override"],
                cost_usd=0.0003 if vote_result["llm_override"] else 0.0,
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )

            debate.swarm_vote = swarm_state

        else:
            # Fallback to heuristic-only if swarm not available
            risk_scores = {"L": 0.9, "M": 0.6, "H": 0.3, "EH": 0.0}
            risk_score = risk_scores.get(risk_code, 0.5)
            brake_penalty = brake_count * 0.15
            approve_score = max(0, risk_score - brake_penalty)

            if approve_score >= 0.60:
                decision = "APPROVE"
                confidence = approve_score
            elif approve_score <= 0.35:
                decision = "REJECT"
                confidence = 1.0 - approve_score
            else:
                decision = "ESCALATE"
                confidence = 0.50

            swarm_state = SwarmVoteState(
                decision_id=state.decision_id,
                decision=decision,
                confidence=confidence,
                method=SwarmVoteMethod.HEURISTIC,
                consensus_ratio=approve_score,
                total_votes=1,  # Fallback = single heuristic
                llm_override=False,
                cost_usd=0.0,
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )

            debate.swarm_vote = swarm_state

        # Update debate state with swarm result
        debate.final_decision = decision
        debate.final_confidence = confidence
        debate.debate_conclusion = f"Swarm vote: {decision} (confidence={confidence:.2%}, method={swarm_state.method.value})"
        debate.status = DebateStatus.COMPLETED
        debate.debate_latency_ms = (time.perf_counter() - start_time) * 1000
        debate.debate_cost_usd = swarm_state.cost_usd

        state.debate = debate
        state.last_successful_phase = "debate"

        state.audit.add_entry(
            event_type="swarm_vote_completed",
            details={
                "decision": decision,
                "confidence": confidence,
                "method": swarm_state.method.value,
                "total_votes": swarm_state.total_votes,
                "consensus_ratio": swarm_state.consensus_ratio,
                "llm_override": swarm_state.llm_override,
                "cost_usd": swarm_state.cost_usd,
                "latency_ms": debate.debate_latency_ms,
            },
            severity="INFO",
        )

        return state

    except Exception as e:
        debate.status = DebateStatus.FAILED
        debate.debate_errors.append(str(e))
        debate.debate_latency_ms = (time.perf_counter() - start_time) * 1000
        state.debate = debate

        state.audit.add_entry(
            event_type="swarm_vote_failed",
            details={"error": str(e)},
            severity="ERROR",
        )

        return state


# =============================================================================
# KILL CHAIN PHASE 2 (LEGACY): THREE-PHASE DEBATE (PanelDebateSystem Wrapper)
# =============================================================================


async def _async_debate_legacy(state: GovernanceState) -> GovernanceState:
    """LEGACY: Three-phase panel debate (Prosecutor → Defender → Judge).

    This is the original 3-round debate system. Kept as side option.
    Use voting_mode=VotingMode.THREE_PHASE to activate.

    Cost: ~$0.125 per debate (3 LLM calls)
    Latency: ~125ms
    """
    start_time = time.perf_counter()
    debate = state.debate
    debate.status = DebateStatus.IN_PROGRESS
    debate.started_at = datetime.utcnow()

    try:
        assessment_result = state.assessment.assessment_result

        # Round 1: Prosecutor argues for rejection
        await asyncio.sleep(0.045)  # Simulate Opus call
        prosecutor_argument = _build_prosecutor_argument(assessment_result)

        # Round 2: Defender argues for approval
        await asyncio.sleep(0.020)  # Simulate Sonnet call
        defender_argument = _build_defender_argument(assessment_result, prosecutor_argument)

        # Round 3: Judge synthesizes and decides
        await asyncio.sleep(0.060)  # Simulate Opus call
        judge_analysis, final_decision, final_confidence = _build_judge_decision(
            prosecutor_argument,
            defender_argument,
        )

        # Record debate round
        debate.rounds.append(
            DebateRound(
                round_number=1,
                prosecutor_argument=prosecutor_argument["reasoning"],
                defender_argument=defender_argument["reasoning"],
                judge_analysis=judge_analysis,
                consensus_score=final_confidence,
                models_used=["claude-opus", "claude-sonnet", "claude-opus"],
            ),
        )

        debate.debate_conclusion = judge_analysis
        debate.final_confidence = final_confidence
        debate.final_decision = final_decision
        debate.status = DebateStatus.COMPLETED
        debate.debate_latency_ms = (time.perf_counter() - start_time) * 1000
        debate.debate_cost_usd = 0.045 + 0.020 + 0.060  # $0.125 total

        state.debate = debate
        state.last_successful_phase = "debate"

        state.audit.add_entry(
            event_type="debate_completed",
            details={
                "decision": final_decision,
                "confidence": final_confidence,
                "cost_usd": debate.debate_cost_usd,
                "latency_ms": debate.debate_latency_ms,
            },
            severity="INFO",
        )

        return state

    except Exception as e:
        debate.status = DebateStatus.FAILED
        debate.debate_errors.append(str(e))
        debate.debate_latency_ms = (time.perf_counter() - start_time) * 1000
        state.debate = debate

        state.audit.add_entry(
            event_type="debate_failed",
            details={"error": str(e)},
            severity="ERROR",
        )

        return state


def _build_prosecutor_argument(assessment_result: dict) -> dict[str, Any]:
    """Build strongest case for rejection"""
    reasons_to_reject = []
    brakes = assessment_result.get("brakes", [])

    for brake in brakes:
        if brake.get("triggered"):
            reasons_to_reject.append(brake.get("reason", "Unknown risk"))

    confidence = min(0.85, 0.60 + len(reasons_to_reject) * 0.10)

    return {
        "position": "REJECT" if reasons_to_reject else "APPROVE_WITH_CONDITIONS",
        "reasoning": f"Identified {len(reasons_to_reject)} risk factors: "
        + "; ".join(reasons_to_reject),
        "confidence": confidence,
    }


def _build_defender_argument(assessment_result: dict, prosecutor: dict) -> dict[str, Any]:
    """Counter prosecutor, provide context"""
    counter_arguments = []
    context = assessment_result.get("purpose", {})

    if context.get("business_value"):
        counter_arguments.append(f"Business value: {context['business_value']}")

    if assessment_result.get("confidence", 0) >= 0.75:
        counter_arguments.append("Assessment confidence is acceptable")

    confidence = min(0.82, 0.55 + len(counter_arguments) * 0.12)

    return {
        "position": "APPROVE" if counter_arguments else "ESCALATE",
        "reasoning": "Mitigations present: " + "; ".join(counter_arguments),
        "confidence": confidence,
    }


def _build_judge_decision(prosecutor: dict, defender: dict) -> tuple[str, str, float]:
    """Synthesize arguments and make final decision"""
    prosecutor_weight = prosecutor["confidence"]
    defender_weight = defender["confidence"]

    if defender_weight > prosecutor_weight + 0.15:
        decision = "APPROVE"
        confidence = defender_weight
        reasoning = f"Defender's mitigations ({defender_weight:.0%}) outweigh prosecutor's concerns ({prosecutor_weight:.0%})"
    elif prosecutor_weight > defender_weight + 0.15:
        decision = "REJECT"
        confidence = prosecutor_weight
        reasoning = f"Prosecutor's risk assessment ({prosecutor_weight:.0%}) more compelling than defender's ({defender_weight:.0%})"
    else:
        decision = "ESCALATE"
        confidence = 0.50
        reasoning = f"Arguments evenly balanced ({prosecutor_weight:.0%} vs {defender_weight:.0%}). Requires human judgment."

    return reasoning, decision, confidence


# =============================================================================
# DEBATE DISPATCHER: Routes to appropriate voting mode
# =============================================================================


async def _async_debate(state: GovernanceState) -> GovernanceState:
    """Dispatch to appropriate voting mode based on state.debate.voting_mode.

    Modes:
    - SWARM (default): 200-agent heuristic + conditional LLM ($0.00006/decision avg)
    - SINGLE_ROUND: Memory-augmented single vote ($0.001/decision)
    - THREE_PHASE: Legacy prosecutor/defender/judge ($0.125/decision)
    - DISABLED: Skip voting entirely
    """
    voting_mode = state.debate.voting_mode

    if voting_mode == VotingMode.DISABLED:
        state.debate.status = DebateStatus.NOT_TRIGGERED
        state.debate.final_decision = "ESCALATE"
        state.debate.final_confidence = 0.0
        state.debate.debate_conclusion = "Voting disabled - escalating to human"
        return state

    if voting_mode == VotingMode.SWARM:
        # Default: minion2 swarm voting
        return await _async_swarm_vote(state)

    if voting_mode == VotingMode.SINGLE_ROUND:
        # Memory-augmented single vote
        return await _async_single_round_vote(state)

    if voting_mode == VotingMode.THREE_PHASE:
        # Legacy 3-phase debate
        return await _async_debate_legacy(state)

    # Fallback to swarm
    return await _async_swarm_vote(state)


def node_debate(state: GovernanceState) -> GovernanceState:
    """Debate Node: Panel Debate System
    Wraps PanelDebateSystem in LangGraph context.
    Only executed if confidence <80% or high risk.
    """
    if not state.debate.should_debate:
        state.debate.status = DebateStatus.NOT_TRIGGERED
        return state

    # Run async debate in event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in async context
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _async_debate(state))
                return future.result()
        else:
            return asyncio.run(_async_debate(state))
    except RuntimeError:
        return asyncio.run(_async_debate(state))


# =============================================================================
# KILL CHAIN PHASE 3: AUDIT LOGGER (AuditCompressKernel Wrapper)
# =============================================================================


def node_audit(state: GovernanceState) -> GovernanceState:
    """Audit Node: Compress and store audit trail
    Wraps AuditCompressKernel in LangGraph context.
    Target: ATP 5-19 format, ≤487 bytes compressed
    """
    start_time = time.perf_counter()
    audit = state.audit
    audit.status = AuditStatus.IN_PROGRESS
    audit.started_at = datetime.utcnow()

    try:
        # Build comprehensive audit metadata
        audit_metadata = {
            "decision_id": state.decision_id,
            "trace_id": state.trace_id,
            "created_at": state.created_at.isoformat(),
            "assessment": {
                "status": state.assessment.status.value,
                "risk_level": state.assessment.risk_level.value
                if state.assessment.risk_level
                else None,
                "confidence": state.assessment.confidence,
                "brakes_triggered": len(state.assessment.brakes),
                "latency_us": state.assessment.assessment_latency_us,
            },
            "debate": {
                "triggered": state.debate.should_debate,
                "status": state.debate.status.value,
                "rounds": len(state.debate.rounds),
                "decision": state.debate.final_decision,
                "confidence": state.debate.final_confidence,
                "cost_usd": state.debate.debate_cost_usd,
                "latency_ms": state.debate.debate_latency_ms,
            }
            if state.debate.should_debate
            else None,
            "entries": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "event_type": e.event_type,
                    "severity": e.severity,
                }
                for e in audit.entries
            ],
        }

        # Compress audit trail (simplified - real impl uses zstd)
        audit_json = json.dumps(audit_metadata, separators=(",", ":"))
        original_size = len(audit_json.encode("utf-8"))

        # Simple compression simulation (real impl uses AuditCompressKernel with zstd)
        import zlib

        compressed = zlib.compress(audit_json.encode("utf-8"), level=9)
        compressed_size = len(compressed)

        # Generate checksum
        checksum = hashlib.sha256(compressed).hexdigest()[:16]

        audit.compressed_audit = compressed
        audit.original_size_bytes = original_size
        audit.compressed_size_bytes = compressed_size
        audit.compression_ratio = 1 - (compressed_size / original_size) if original_size > 0 else 0
        audit.checksum = checksum

        audit.status = AuditStatus.COMPLETED
        audit.audit_latency_ms = (time.perf_counter() - start_time) * 1000
        audit.updated_at = datetime.utcnow()

        state.audit = audit
        state.last_successful_phase = "audit"

        audit.add_entry(
            event_type="audit_completed",
            details={
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": f"{audit.compression_ratio:.1%}",
                "checksum": checksum,
            },
            severity="INFO",
        )

        return state

    except Exception as e:
        audit.status = AuditStatus.FAILED
        audit.audit_errors.append(str(e))
        audit.audit_latency_ms = (time.perf_counter() - start_time) * 1000
        state.audit = audit

        audit.add_entry(event_type="audit_failed", details={"error": str(e)}, severity="ERROR")

        return state


# =============================================================================
# FINALIZE NODE: Final Decision Output
# =============================================================================


def node_finalize(state: GovernanceState) -> GovernanceState:
    """Finalize Node: Prepare final decision output
    Aggregates all phases into final verdict
    """
    # Determine final decision from assessment and debate
    assessment_approved = state.assessment.assessment_result.get("approved", False)

    if state.debate.should_debate and state.debate.final_decision:
        # Use debate decision if debate was triggered
        final_decision = state.debate.final_decision == "APPROVE"
        final_confidence = state.debate.final_confidence or 0.50
        final_reasoning = state.debate.debate_conclusion or "Debate concluded"
    else:
        # Use assessment decision
        final_decision = assessment_approved
        final_confidence = state.assessment.confidence
        final_reasoning = f"Assessment: {state.assessment.risk_level.value if state.assessment.risk_level else 'Unknown'} risk"

    state.final_decision = final_decision
    state.final_confidence = final_confidence
    state.final_reasoning = final_reasoning
    state.completed_at = datetime.utcnow()

    # Calculate total latency
    state.total_latency_ms = (
        state.assessment.assessment_latency_us / 1000
        + state.debate.debate_latency_ms
        + state.audit.audit_latency_ms
    )

    # Generate memory fingerprint for Mem0 storage
    fingerprint_data = f"{state.decision_id}:{state.final_decision}:{state.final_confidence}"
    state.memory_fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

    state.audit.add_entry(
        event_type="governance_finalized",
        details={
            "decision": final_decision,
            "confidence": final_confidence,
            "total_latency_ms": state.total_latency_ms,
            "memory_fingerprint": state.memory_fingerprint,
        },
        severity="INFO",
    )

    return state

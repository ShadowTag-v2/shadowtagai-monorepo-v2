/**
 * V23 KAIROS Daemon — TypeScript Companion
 * Tasks 4, 11: AsyncSuggestionConsumer + OpenTelemetry spans
 *
 * This is the Bun-native daemon that runs alongside the Python
 * KAIROS daemon (scripts/kairos_daemon.py). It handles the
 * TypeScript routing layer, teleportation bridge, and OTel
 * instrumentation for cast_vote() tracing.
 */

import { autoRoute } from "../tools/cognitive_router/dispatch";
import { resolveFlag } from "../config/feature_flags";
import {
  createEnvelope,
  castVote,
  type VoteRecord,
  type RiskLevel,
} from "../tools/mailbox/policies";
import { startTeleportationBridge, teleportPlanToBrowser } from "../tools/teleportation/bridge";

/** Lightweight OTel-compatible span for cast_vote tracing (Task 11) */
interface Span {
  name: string;
  startTime: number;
  endTime?: number;
  attributes: Record<string, string | number | boolean>;
  events: Array<{ name: string; timestamp: number; attributes?: Record<string, unknown> }>;
}

const spans: Span[] = [];

function startSpan(name: string, attrs: Record<string, string | number | boolean> = {}): Span {
  const span: Span = {
    name,
    startTime: performance.now(),
    attributes: attrs,
    events: [],
  };
  spans.push(span);
  return span;
}

function endSpan(span: Span): void {
  span.endTime = performance.now();
}

function addSpanEvent(span: Span, name: string, attrs?: Record<string, unknown>): void {
  span.events.push({ name, timestamp: performance.now(), attributes: attrs });
}

/** Instrumented cast_vote wrapper with OTel span (Task 11) */
function instrumentedCastVote(
  planId: string,
  riskLevel: RiskLevel,
  vote: VoteRecord,
): { accepted: boolean; span: Span } {
  const span = startSpan("AgentMailbox.cast_vote", {
    "mailbox.plan_id": planId,
    "mailbox.agent": vote.agent,
    "mailbox.vote": vote.vote,
    "mailbox.risk_level": riskLevel,
  });

  addSpanEvent(span, "vote_received", {
    confidence: vote.confidence,
    latency_ms: vote.latency_ms,
  });

  const envelope = createEnvelope(planId, riskLevel);
  const accepted = castVote(envelope, vote);

  span.attributes["mailbox.accepted"] = accepted;
  span.attributes["mailbox.envelope_status"] = envelope.status;

  addSpanEvent(span, "vote_processed", {
    final_status: envelope.status,
    vote_count: envelope.votes.length,
  });

  endSpan(span);
  return { accepted, span };
}

/** Suggestion queue — async in-memory buffer (Task 4) */
interface Suggestion {
  id: string;
  text: string;
  score: number;
  timestamp: number;
}

class AsyncSuggestionQueue {
  private queue: Suggestion[] = [];
  private maxSize: number;
  private consumed = 0;
  private dismissed = 0;

  constructor(maxSize = 100) {
    this.maxSize = maxSize;
  }

  publish(suggestion: Suggestion): void {
    if (this.queue.length >= this.maxSize) {
      this.queue.shift(); // Drop oldest
    }
    this.queue.push(suggestion);
  }

  consume(): Suggestion | null {
    const item = this.queue.shift() ?? null;
    if (item) this.consumed++;
    return item;
  }

  dismiss(): void {
    this.dismissed++;
    this.queue.shift();
  }

  get stats() {
    return {
      pending: this.queue.length,
      consumed: this.consumed,
      dismissed: this.dismissed,
      total: this.consumed + this.dismissed + this.queue.length,
    };
  }
}

/** Main daemon loop */
async function kairosHeartbeat(): Promise<void> {
  const suggestionQueue = new AsyncSuggestionQueue();
  let teleportBridge: { stop: () => void } | null = null;

  // Start teleportation bridge if enabled
  if (resolveFlag("TELEPORTATION_PROTOCOL_V1")) {
    teleportBridge = startTeleportationBridge(9876);
    console.log("⚡ [KAIROS] Teleportation bridge started on ws://localhost:9876");
  }

  console.log("⚡ [KAIROS-TS] Daemon heartbeat started");
  console.log(`   SEMANTIC_ROUTING: ${resolveFlag("SEMANTIC_ROUTING")}`);
  console.log(`   TELEPORTATION: ${resolveFlag("TELEPORTATION_PROTOCOL_V1")}`);
  console.log(`   ASYNC_BATCHING: ${resolveFlag("ASYNC_CONSUMER_BATCHING")}`);

  // Simulate a single heartbeat cycle for testing
  const testInput = "plan the architecture for V24 migration";
  const routeResult = await autoRoute(testInput);

  console.log(`   Route result: ${routeResult.intent} (${routeResult.classifier}, ${routeResult.latency_ms.toFixed(2)}ms)`);

  // Publish a suggestion
  suggestionQueue.publish({
    id: crypto.randomUUID(),
    text: `Consider: ${routeResult.intent} detected for input`,
    score: routeResult.confidence,
    timestamp: Date.now(),
  });

  // Process the suggestion
  const suggestion = suggestionQueue.consume();
  if (suggestion) {
    console.log(`   Consumed suggestion: ${suggestion.text} (score: ${suggestion.score})`);

    // If it's a plan, route through mailbox
    if (routeResult.intent === "PLAN_REQUEST") {
      const voteResult = instrumentedCastVote(
        suggestion.id,
        "medium",
        {
          agent: "architecture_board",
          vote: "approve",
          confidence: 0.92,
          reasoning: "Plan aligns with V23 architecture",
          timestamp: Date.now(),
          latency_ms: 12,
        },
      );
      console.log(`   Mailbox vote: ${voteResult.accepted ? "accepted" : "rejected"} (${voteResult.span.attributes["mailbox.envelope_status"]})`);

      // Teleport plan to browser if bridge is active
      if (teleportBridge) {
        teleportPlanToBrowser(suggestion.id, {
          intent: routeResult.intent,
          text: testInput,
          confidence: routeResult.confidence,
        });
        console.log("   Plan teleported to browser for visualization");
      }
    }
  }

  console.log(`   Queue stats: ${JSON.stringify(suggestionQueue.stats)}`);
  console.log(`   OTel spans captured: ${spans.length}`);

  // Cleanup
  if (teleportBridge) teleportBridge.stop();
  console.log("⚡ [KAIROS-TS] Heartbeat cycle complete");
}

// Export for testing
export {
  kairosHeartbeat,
  instrumentedCastVote,
  AsyncSuggestionQueue,
  spans as capturedSpans,
};

// Run if executed directly
if (import.meta.main) {
  await kairosHeartbeat();
}

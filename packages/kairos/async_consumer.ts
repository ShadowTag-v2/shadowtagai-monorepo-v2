/**
 * V23 Async Suggestion Consumer — Tasks 4 & 11
 * Polls the KAIROS mailbox for agent votes via Google Cloud Pub/Sub.
 * Wraps all operations in OpenTelemetry spans for distributed tracing.
 */

import { type Message, PubSub } from "@google-cloud/pubsub";
import { type Span, trace } from "@opentelemetry/api";

const PROJECT_ID = "shadowtag-omega-v4";
const SUBSCRIPTION_NAME = "kairos-mailbox-sub";
const CONSENSUS_THRESHOLD = 0.85;

const tracer = trace.getTracer("kairos-mailbox-tracer", "23.0.0");

export interface VoteMessage {
  agentId: string;
  planId: string;
  confidence: number;
  intent: string;
  timestamp: number;
}

export class AsyncSuggestionConsumer {
  private pubsub: PubSub;
  private isListening = false;
  private voteBuffer: VoteMessage[] = [];

  constructor(projectId: string = PROJECT_ID) {
    this.pubsub = new PubSub({ projectId });
  }

  startListening(): void {
    if (this.isListening) return;
    this.isListening = true;

    tracer.startActiveSpan("consume_mailbox_votes", (span: Span) => {
      console.log("⚡ [KAIROS] Polling asynchronous mailbox policies...");

      const subscription = this.pubsub.subscription(SUBSCRIPTION_NAME);

      subscription.on("message", (message: Message) => {
        try {
          const vote: VoteMessage = JSON.parse(message.data.toString());

          span.addEvent("vote_received", {
            "agent.id": vote.agentId,
            "plan.id": vote.planId,
            "vote.confidence": vote.confidence,
          });

          this.voteBuffer.push(vote);

          if (vote.confidence >= CONSENSUS_THRESHOLD) {
            span.addEvent("consensus_reached", {
              "consensus.threshold": CONSENSUS_THRESHOLD,
              "vote.confidence": vote.confidence,
            });
            console.log(
              `✅ [KAIROS] Consensus reached: ${vote.confidence} >= ${CONSENSUS_THRESHOLD}`,
            );
          }

          message.ack();
        } catch {
          message.nack();
        }
      });

      subscription.on("error", (error: Error) => {
        span.recordException(error);
        console.error(`❌ [KAIROS] Subscription error: ${error.message}`);
      });

      span.end();
    });
  }

  getVoteBuffer(): VoteMessage[] {
    return [...this.voteBuffer];
  }

  clearVoteBuffer(): void {
    this.voteBuffer = [];
  }

  stop(): void {
    this.isListening = false;
    console.log("⚡ [KAIROS] Mailbox consumer stopped.");
  }
}

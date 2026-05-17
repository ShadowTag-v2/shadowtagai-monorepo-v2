/**
 * V23 Teleportation Protocol — PubSub-based CLI↔Browser Bridge
 * Task 12 & 15: Alternative transport using Google Cloud Pub/Sub
 * for environments where direct WebSocket is unavailable.
 *
 * Primary bridge: tools/teleportation/bridge.ts (Bun.serve WebSocket)
 * This module: Pub/Sub fallback for Cloud Run deployments.
 */

import { type Message, PubSub } from "@google-cloud/pubsub";

const PROJECT_ID = "shadowtag-omega-v4";
const TELEPORT_TOPIC = "teleport-commands";

export interface TeleportCommand {
  action: string;
  payload: Record<string, unknown>;
  source: "cli" | "browser";
  timestamp: number;
}

export class TeleportationProtocol {
  private pubsub: PubSub;

  constructor(projectId: string = PROJECT_ID) {
    this.pubsub = new PubSub({ projectId });
  }

  async sendToBrowser(action: string, payload: Record<string, unknown>): Promise<string> {
    console.log(`⚡ [Teleport] Sending CLI action '${action}' to Chrome DevTools MCP...`);

    const command: TeleportCommand = {
      action,
      payload,
      source: "cli",
      timestamp: Date.now(),
    };

    const messageId = await this.pubsub.topic(TELEPORT_TOPIC).publishMessage({
      data: Buffer.from(JSON.stringify(command)),
      attributes: { action, source: "cli" },
    });

    console.log(`✅ [Teleport] Message ${messageId} published to ${TELEPORT_TOPIC}`);
    return messageId;
  }

  async sendToCli(action: string, payload: Record<string, unknown>): Promise<string> {
    const command: TeleportCommand = {
      action,
      payload,
      source: "browser",
      timestamp: Date.now(),
    };

    return this.pubsub.topic(TELEPORT_TOPIC).publishMessage({
      data: Buffer.from(JSON.stringify(command)),
      attributes: { action, source: "browser" },
    });
  }

  listenForCommands(subscriptionName: string, handler: (command: TeleportCommand) => void): void {
    const subscription = this.pubsub.subscription(subscriptionName);

    subscription.on("message", (message: Message) => {
      try {
        const command: TeleportCommand = JSON.parse(message.data.toString());
        handler(command);
        message.ack();
      } catch {
        message.nack();
      }
    });
  }
}

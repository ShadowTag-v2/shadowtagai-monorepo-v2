/**
 * V23 Teleportation Protocol — CLI ↔ Browser Plan Handoff
 * Task 12: WebSocket bridge between CLI agent and Chrome DevTools MCP
 *
 * Uses Bun.serve() for native WebSocket support. No external deps.
 * The CLI publishes plan artifacts; the browser consumes them for
 * visual rendering via Stitch MCP screen generation.
 */

/** Plan artifact structure for teleportation */
export interface TeleportPayload {
  action: "PLAN_PREVIEW" | "PLAN_APPROVE" | "PLAN_REJECT" | "PLAN_VISUALIZE";
  planId: string;
  payload: Record<string, unknown>;
  timestamp: number;
  source: "cli" | "browser";
}

/** Connected client tracking */
const connectedClients = new Set<{
  ws: unknown; // Bun WebSocket type
  clientType: "cli" | "browser";
  connectedAt: number;
}>();

/** Message history for late-joining clients */
const messageBuffer: TeleportPayload[] = [];
const MAX_BUFFER_SIZE = 50;

/**
 * Broadcast a teleport payload to all connected clients
 * of a specific type, or to all if no type specified.
 */
function broadcast(
  payload: TeleportPayload,
  targetType?: "cli" | "browser",
): void {
  const serialized = JSON.stringify(payload);

  // Buffer the message for late joiners
  messageBuffer.push(payload);
  if (messageBuffer.length > MAX_BUFFER_SIZE) {
    messageBuffer.shift();
  }

  for (const client of connectedClients) {
    if (!targetType || client.clientType === targetType) {
      try {
        (client.ws as { send: (data: string) => void }).send(serialized);
      } catch {
        // Client disconnected, will be cleaned up
        connectedClients.delete(client);
      }
    }
  }
}

/**
 * Send a plan from CLI to browser for visualization.
 * This is the primary teleportation entry point.
 */
export function teleportPlanToBrowser(
  planId: string,
  planData: Record<string, unknown>,
): void {
  broadcast(
    {
      action: "PLAN_VISUALIZE",
      planId,
      payload: planData,
      timestamp: Date.now(),
      source: "cli",
    },
    "browser",
  );
}

/**
 * Send an approval/rejection from browser back to CLI.
 */
export function teleportApprovalToCli(
  planId: string,
  approved: boolean,
): void {
  broadcast(
    {
      action: approved ? "PLAN_APPROVE" : "PLAN_REJECT",
      planId,
      payload: { approved },
      timestamp: Date.now(),
      source: "browser",
    },
    "cli",
  );
}

/**
 * Start the Teleportation Bridge WebSocket server.
 * Default port: 9876
 */
export function startTeleportationBridge(port = 9876): { stop: () => void } {
  const server = Bun.serve({
    port,
    fetch(req, server) {
      const url = new URL(req.url);

      // Health check endpoint
      if (url.pathname === "/health") {
        return new Response(
          JSON.stringify({
            status: "ok",
            clients: connectedClients.size,
            buffered: messageBuffer.length,
            uptime_ms: Date.now() - startTime,
          }),
          { headers: { "Content-Type": "application/json" } },
        );
      }

      // WebSocket upgrade
      const clientType = url.searchParams.get("type") as
        | "cli"
        | "browser"
        | null;
      if (!clientType || !["cli", "browser"].includes(clientType)) {
        return new Response("Missing ?type=cli|browser", { status: 400 });
      }

      const upgraded = server.upgrade(req, { data: { clientType } });
      if (!upgraded) {
        return new Response("WebSocket upgrade failed", { status: 500 });
      }
      return undefined;
    },
    websocket: {
      open(ws) {
        const clientType = (ws.data as { clientType: "cli" | "browser" })
          .clientType;
        const client = { ws, clientType, connectedAt: Date.now() };
        connectedClients.add(client);

        // Send buffered messages to late-joining client
        for (const msg of messageBuffer) {
          (ws as unknown as { send: (data: string) => void }).send(
            JSON.stringify(msg),
          );
        }
      },
      message(ws, message) {
        try {
          const payload = JSON.parse(String(message)) as TeleportPayload;
          // Relay to the opposite client type
          const targetType =
            payload.source === "cli" ? "browser" : "cli";
          broadcast(payload, targetType);
        } catch {
          // Malformed message — drop silently
        }
      },
      close(ws) {
        for (const client of connectedClients) {
          if (client.ws === ws) {
            connectedClients.delete(client);
            break;
          }
        }
      },
    },
  });

  const startTime = Date.now();
  return { stop: () => server.stop() };
}

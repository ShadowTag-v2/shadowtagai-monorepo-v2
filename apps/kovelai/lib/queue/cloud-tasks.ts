/**
 * @fileoverview Cloud Tasks Queue — War Room Pipeline Enqueue
 *
 * Wraps Google Cloud Tasks HTTP targets for the Murder Board pipeline.
 * Each stage gets its own task with idempotency keys to prevent
 * duplicate execution during retries.
 *
 * Queue: kovelai-murder-board (us-central1)
 * Target: Cloud Run counselconduit-api
 *
 * @see WAR_ROOM_ARCHITECTURE.md — Pipeline stages
 * @see murder-board.ts — Pipeline orchestrator
 */

// NOTE: In production, this uses @google-cloud/tasks.
// For development, we use direct function calls (see murder-board.ts).

export interface CloudTaskPayload {
  sessionId: string;
  stage: number;
  firmId: string;
  retryCount?: number;
}

/**
 * Cloud Tasks queue configuration.
 */
const QUEUE_CONFIG = {
  project: process.env.GCP_PROJECT_ID || "shadowtag-omega-v4",
  location: "us-central1",
  queue: "kovelai-murder-board",
  targetUrl: process.env.CLOUD_RUN_URL || "https://counselconduit-767252945109.us-central1.run.app",
} as const;

/**
 * Stage-specific routing configuration.
 */
const STAGE_ROUTES: Record<number, { path: string; timeoutSeconds: number }> = {
  1: { path: "/api/war-room/stages/intake", timeoutSeconds: 30 },
  2: { path: "/api/war-room/stages/osint", timeoutSeconds: 60 },
  3: { path: "/api/war-room/stages/verb-audit", timeoutSeconds: 45 },
  4: { path: "/api/war-room/stages/oracle", timeoutSeconds: 120 },
  5: { path: "/api/war-room/stages/citations", timeoutSeconds: 90 },
  6: { path: "/api/war-room/stages/brief", timeoutSeconds: 60 },
  7: { path: "/api/war-room/stages/vault", timeoutSeconds: 30 },
};

/**
 * Enqueue a pipeline stage via Cloud Tasks.
 *
 * Production: Creates an HTTP task targeting Cloud Run.
 * Development: Falls through to direct invocation.
 */
export async function enqueueStage(payload: CloudTaskPayload): Promise<string> {
  const route = STAGE_ROUTES[payload.stage];
  if (!route) {
    throw new Error(`Invalid stage: ${payload.stage}`);
  }

  if (process.env.NODE_ENV !== "production") {
    // Development: return a mock task ID
    console.log(`[DEV] Would enqueue stage ${payload.stage} for session ${payload.sessionId}`);
    return `dev-task-${payload.sessionId}-stage-${payload.stage}`;
  }

  // Production: Use Cloud Tasks API
  // Dynamic import to avoid bundling in dev
  const { CloudTasksClient } = await import("@google-cloud/tasks");
  const client = new CloudTasksClient();

  const parent = client.queuePath(QUEUE_CONFIG.project, QUEUE_CONFIG.location, QUEUE_CONFIG.queue);

  const idempotencyKey = `${payload.sessionId}-stage-${payload.stage}-${Date.now()}`;

  const [response] = await client.createTask({
    parent,
    task: {
      name: `${parent}/tasks/${idempotencyKey}`,
      httpRequest: {
        httpMethod: "POST",
        url: `${QUEUE_CONFIG.targetUrl}${route.path}`,
        headers: {
          "Content-Type": "application/json",
          "X-War-Room-Session": payload.sessionId,
          "X-Idempotency-Key": idempotencyKey,
        },
        body: Buffer.from(JSON.stringify(payload)).toString("base64"),
      },
      scheduleTime: {
        seconds: Math.floor(Date.now() / 1000),
      },
      dispatchDeadline: {
        seconds: route.timeoutSeconds,
      },
    },
  });

  return response.name || idempotencyKey;
}

/**
 * Enqueue the next stage in the pipeline.
 */
export async function enqueueNextStage(
  sessionId: string,
  currentStage: number,
  firmId: string,
): Promise<string | null> {
  const nextStage = currentStage + 1;
  if (nextStage > 7) {
    return null; // Pipeline complete
  }
  return enqueueStage({
    sessionId,
    stage: nextStage,
    firmId,
  });
}

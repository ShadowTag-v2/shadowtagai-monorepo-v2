/**
 * GDPR TTL Cloud Tasks Scheduler
 *
 * Item #16: GDPR 30-day data deletion via Cloud Tasks.
 *
 * Creates Cloud Tasks that fire after 30 days to delete:
 * - Ephemeral session transcripts
 * - Client search queries
 * - Intent Vault signals
 * - S.E.U. token logs
 *
 * This is the enforcement mechanism for the "Dead Man's Switch"
 * at the data layer. Kovel receipts are RETAINED (they contain
 * no content, only hashes).
 *
 * @see app/api/internal/gdpr-ttl/route.ts
 */

import { z } from 'zod';

// ─── Types ──────────────────────────────────────────────────────────

export interface GDPRDeletionTask {
  taskId: string;
  firmId: string;
  sessionId: string;
  dataType: 'transcript' | 'search_query' | 'intent_signal' | 'seu_log' | 'full_session';
  scheduledDeletionAt: string; // ISO datetime
  createdAt: string;
  firestorePaths: string[];
  retainKovelReceipt: boolean;
}

const GDPRDeletionRequestSchema = z.object({
  firmId: z.string().uuid(),
  sessionId: z.string().uuid(),
  dataType: z.enum(['transcript', 'search_query', 'intent_signal', 'seu_log', 'full_session']),
  retentionDays: z.number().int().min(1).max(365).default(30),
});

export type GDPRDeletionRequest = z.infer<typeof GDPRDeletionRequestSchema>;

// ─── Firestore Path Mapping ─────────────────────────────────────────

const DATA_TYPE_PATHS: Record<string, (firmId: string, sessionId: string) => string[]> = {
  transcript: (firmId, sessionId) => [`firms/${firmId}/sessions/${sessionId}/transcripts`],
  search_query: (firmId, sessionId) => [`firms/${firmId}/sessions/${sessionId}/queries`],
  intent_signal: (firmId, sessionId) => [
    `firms/${firmId}/sessions/${sessionId}/intents`,
    `firms/${firmId}/intent_vault/${sessionId}`,
  ],
  seu_log: (firmId, sessionId) => [`firms/${firmId}/sessions/${sessionId}/tokens`],
  full_session: (firmId, sessionId) => [`firms/${firmId}/sessions/${sessionId}`],
};

// ─── Task Generator ─────────────────────────────────────────────────

/**
 * Creates a GDPR deletion task payload for Cloud Tasks.
 */
export function createDeletionTask(request: GDPRDeletionRequest): GDPRDeletionTask {
  const parsed = GDPRDeletionRequestSchema.parse(request);
  const now = new Date();
  const deletionDate = new Date(now.getTime() + parsed.retentionDays * 24 * 60 * 60 * 1000);

  const pathGenerator = DATA_TYPE_PATHS[parsed.dataType];
  const paths = pathGenerator ? pathGenerator(parsed.firmId, parsed.sessionId) : [];

  return {
    taskId: `gdpr-${parsed.dataType}-${parsed.sessionId}-${now.getTime()}`,
    firmId: parsed.firmId,
    sessionId: parsed.sessionId,
    dataType: parsed.dataType,
    scheduledDeletionAt: deletionDate.toISOString(),
    createdAt: now.toISOString(),
    firestorePaths: paths,
    retainKovelReceipt: true, // Always retain — receipts contain only hashes
  };
}

/**
 * Schedules a full session cleanup — creates tasks for ALL data types.
 */
export function scheduleFullSessionCleanup(
  firmId: string,
  sessionId: string,
  retentionDays = 30,
): GDPRDeletionTask[] {
  const dataTypes = ['transcript', 'search_query', 'intent_signal', 'seu_log'] as const;

  return dataTypes.map((dataType) =>
    createDeletionTask({
      firmId,
      sessionId,
      dataType,
      retentionDays,
    }),
  );
}

/**
 * Enqueues deletion tasks to Cloud Tasks.
 *
 * @param tasks - Array of deletion tasks to enqueue
 * @returns Object with success count and any errors
 */
export async function enqueueDeletionTasks(
  tasks: GDPRDeletionTask[],
): Promise<{ enqueued: number; errors: string[] }> {
  const cloudTasksUrl = process.env.CLOUD_TASKS_QUEUE_URL;
  const queuePath =
    process.env.GDPR_QUEUE_PATH ??
    'projects/shadowtag-omega-v4/locations/us-central1/queues/gdpr-deletion';

  if (!cloudTasksUrl) {
    return { enqueued: 0, errors: ['CLOUD_TASKS_QUEUE_URL not configured'] };
  }

  const results = { enqueued: 0, errors: [] as string[] };

  for (const task of tasks) {
    try {
      const scheduleTime = new Date(task.scheduledDeletionAt);

      const res = await fetch(cloudTasksUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${process.env.CLOUD_TASKS_SERVICE_TOKEN ?? ''}`,
        },
        body: JSON.stringify({
          parent: queuePath,
          task: {
            name: `${queuePath}/tasks/${task.taskId}`,
            scheduleTime: scheduleTime.toISOString(),
            httpRequest: {
              httpMethod: 'POST',
              url: `${process.env.NEXT_PUBLIC_APP_URL ?? ''}/api/internal/gdpr-ttl`,
              headers: {
                'Content-Type': 'application/json',
              },
              body: Buffer.from(
                JSON.stringify({
                  taskId: task.taskId,
                  firmId: task.firmId,
                  sessionId: task.sessionId,
                  dataType: task.dataType,
                  firestorePaths: task.firestorePaths,
                  retainKovelReceipt: task.retainKovelReceipt,
                }),
              ).toString('base64'),
            },
          },
        }),
        signal: AbortSignal.timeout(10000),
      });

      if (res.ok) {
        results.enqueued++;
      } else {
        const errText = await res.text();
        results.errors.push(`Task ${task.taskId}: ${res.status} — ${errText}`);
      }
    } catch (err) {
      results.errors.push(
        `Task ${task.taskId}: ${err instanceof Error ? err.message : String(err)}`,
      );
    }
  }

  return results;
}

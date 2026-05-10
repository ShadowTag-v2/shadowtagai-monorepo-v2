/**
 * V19 Jules Bridge — Asynchronous CI/CD Connector
 *
 * Wires the Jules SDK for background code review, issue triage,
 * and autonomous PR generation. Jules operates as an asynchronous
 * workforce agent dispatched by the Archon core.
 *
 * Runtime: Bun
 * Project: shadowtag-omega-v4
 */

// ─── Types ────────────────────────────────────────────────────────
interface JulesTask {
  taskId: string;
  type: 'code_review' | 'issue_triage' | 'pr_generation' | 'refactor';
  repository: string;
  branch: string;
  prompt: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  createdAt: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
}

interface JulesResult {
  taskId: string;
  status: 'completed' | 'failed';
  output: string;
  prUrl?: string;
  filesChanged: string[];
  duration_ms: number;
}

// ─── Configuration ────────────────────────────────────────────────
const JULES_API_BASE = 'https://jules.googleapis.com/v1beta';
const REPO = 'ShadowTag-v2/Monorepo-Uphillsnowball';
const DEFAULT_BRANCH = 'main';

/**
 * Dispatch a task to the Jules asynchronous workforce.
 * Returns a task ID for polling completion status.
 */
export async function dispatchJulesTask(
  type: JulesTask['type'],
  prompt: string,
  options: {
    branch?: string;
    priority?: JulesTask['priority'];
    files?: string[];
  } = {}
): Promise<string> {
  const task: JulesTask = {
    taskId: crypto.randomUUID(),
    type,
    repository: REPO,
    branch: options.branch ?? DEFAULT_BRANCH,
    prompt,
    priority: options.priority ?? 'medium',
    createdAt: new Date().toISOString(),
    status: 'queued',
  };

  console.log(
    `⚡ [Jules] Dispatching ${type} task: ${task.taskId} (${task.priority})`
  );

  // Queue the task via Jules API (Cloud Tasks integration)
  const response = await fetch(`${JULES_API_BASE}/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${await getServiceAccountToken()}`,
    },
    body: JSON.stringify({
      task_type: type,
      repository: REPO,
      branch: task.branch,
      instructions: prompt,
      scope: options.files ?? [],
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Jules API error (${response.status}): ${errorText}`);
  }

  const result = await response.json();
  console.log(`⚡ [Jules] Task queued: ${result.name ?? task.taskId}`);
  return result.name ?? task.taskId;
}

/**
 * Poll Jules task status until completion or timeout.
 */
export async function pollJulesTask(
  taskName: string,
  timeoutMs: number = 300000
): Promise<JulesResult> {
  const startTime = Date.now();
  const POLL_INTERVAL = 10000;

  while (Date.now() - startTime < timeoutMs) {
    const response = await fetch(`${JULES_API_BASE}/tasks/${taskName}`, {
      headers: {
        Authorization: `Bearer ${await getServiceAccountToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Jules poll error (${response.status})`);
    }

    const status = await response.json();

    if (status.state === 'SUCCEEDED' || status.state === 'FAILED') {
      return {
        taskId: taskName,
        status: status.state === 'SUCCEEDED' ? 'completed' : 'failed',
        output: status.result?.summary ?? '',
        prUrl: status.result?.pull_request_url,
        filesChanged: status.result?.files_changed ?? [],
        duration_ms: Date.now() - startTime,
      };
    }

    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL));
  }

  throw new Error(`Jules task ${taskName} timed out after ${timeoutMs}ms`);
}

/**
 * Dispatch a code review task and wait for the result.
 */
export async function reviewCode(
  files: string[],
  instructions: string = 'Review for security, performance, and code quality.'
): Promise<JulesResult> {
  const taskName = await dispatchJulesTask('code_review', instructions, {
    files,
    priority: 'high',
  });
  return pollJulesTask(taskName);
}

/**
 * Get a service account token for Jules API authentication.
 * Uses Application Default Credentials (ADC) via the metadata server.
 */
async function getServiceAccountToken(): Promise<string> {
  // In Cloud Run / GKE, use the metadata server
  const metadataUrl =
    'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token';

  try {
    const response = await fetch(metadataUrl, {
      headers: { 'Metadata-Flavor': 'Google' },
    });
    if (response.ok) {
      const data = await response.json();
      return data.access_token;
    }
  } catch {
    // Not on GCP — fall back to gcloud
  }

  // Local fallback: use gcloud auth
  const proc = Bun.spawnSync(['gcloud', 'auth', 'print-access-token']);
  return proc.stdout.toString().trim();
}

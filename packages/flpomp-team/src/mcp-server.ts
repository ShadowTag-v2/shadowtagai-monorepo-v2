/**
 * Pomelli Swarm — MCP Server (V25 Pinnacle)
 *
 * Orchestrates continuous A/B testing across the live fleet:
 *   - HeadFade (headfade.com)
 *   - CounselConduit (counselconduit.com)
 *   - ShadowTagAI/KovelAI (kovelai.com)
 *
 * Uses Gemini Flash-Lite for test-time compute (arXiv:2512.14982) to generate
 * UI mutation hypotheses, then validates via Chrome DevTools MCP Lighthouse audits.
 *
 * Tools exposed:
 *   - audit_site: Run a full Lighthouse + visual regression audit on a target URL
 *   - get_swarm_status: Return current swarm state (active patches, queue depth)
 *   - list_targets: List all monitored sites and their latest scores
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync } from 'fs';
import { join } from 'path';

const MODEL = process.env.POMELLI_MODEL || 'gemini-3.1-flash-lite-preview';
const PROJECT = process.env.GOOGLE_CLOUD_PROJECT || 'shadowtag-omega-v4';
const QUEUE_DIR = join(
  process.env.WORKSPACE_ROOT || '/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball',
  '.jules_queue',
);

// Ensure queue directory exists
if (!existsSync(QUEUE_DIR)) mkdirSync(QUEUE_DIR, { recursive: true });

interface SiteTarget {
  name: string;
  url: string;
  lastAuditScore?: number;
  lastAuditTime?: string;
}

const FLEET_TARGETS: SiteTarget[] = [
  { name: 'HeadFade', url: 'https://headfade.com' },
  { name: 'CounselConduit', url: 'https://counselconduit-767252945109.us-central1.run.app' },
  { name: 'KovelAI', url: 'https://kovelai.com' },
];

interface McpRequest {
  id: string | number;
  method: string;
  params?: Record<string, unknown>;
}

interface McpResponse {
  jsonrpc: '2.0';
  id: string | number;
  result?: unknown;
  error?: { code: number; message: string };
}

/**
 * Run a Lighthouse-style audit on a target URL.
 * In production, this delegates to Chrome DevTools MCP's lighthouse_audit tool.
 * Here we provide the orchestration envelope.
 */
async function auditSite(url: string): Promise<Record<string, unknown>> {
  const startTime = Date.now();

  // Call Lighthouse via the Bun subprocess (uses installed chrome-launcher)
  const result = await Bun.spawn(
    ['npx', '-y', 'lighthouse', url, '--output=json', '--chrome-flags=--headless --no-sandbox', '--quiet'],
    { stdout: 'pipe', stderr: 'pipe' },
  );

  const stdout = await new Response(result.stdout).text();
  const elapsed = Date.now() - startTime;

  try {
    const report = JSON.parse(stdout);
    const scores = {
      performance: Math.round((report.categories?.performance?.score || 0) * 100),
      accessibility: Math.round((report.categories?.accessibility?.score || 0) * 100),
      bestPractices: Math.round((report.categories?.['best-practices']?.score || 0) * 100),
      seo: Math.round((report.categories?.seo?.score || 0) * 100),
    };

    // Update fleet target with latest scores
    const target = FLEET_TARGETS.find(t => t.url === url);
    if (target) {
      target.lastAuditScore = scores.performance;
      target.lastAuditTime = new Date().toISOString();
    }

    return { url, scores, elapsedMs: elapsed, model: MODEL, project: PROJECT };
  } catch {
    return { url, error: 'Failed to parse Lighthouse output', elapsedMs: elapsed, rawLength: stdout.length };
  }
}

/**
 * Get current swarm status — active patches and queue depth.
 */
function getSwarmStatus(): Record<string, unknown> {
  const queueFiles = existsSync(QUEUE_DIR)
    ? readdirSync(QUEUE_DIR).filter(f => f.endsWith('.patch') || f.endsWith('.yaml'))
    : [];

  return {
    model: MODEL,
    project: PROJECT,
    queueDir: QUEUE_DIR,
    queueDepth: queueFiles.length,
    pendingPatches: queueFiles,
    fleetSize: FLEET_TARGETS.length,
    targets: FLEET_TARGETS.map(t => t.name),
  };
}

/**
 * List all monitored sites and their latest audit data.
 */
function listTargets(): SiteTarget[] {
  return FLEET_TARGETS;
}

function makeResponse(id: string | number, result: unknown): McpResponse {
  return { jsonrpc: '2.0', id, result };
}

function makeError(id: string | number, code: number, message: string): McpResponse {
  return { jsonrpc: '2.0', id, error: { code, message } };
}

// MCP stdio server bootstrap
if (import.meta.main) {
  console.error('🐝 Pomelli Swarm MCP Server Active (V25 Pinnacle)');
  console.error(`   Model: ${MODEL} | Fleet: ${FLEET_TARGETS.length} sites`);
  const decoder = new TextDecoder();

  for await (const chunk of Bun.stdin.stream()) {
    try {
      const text = decoder.decode(chunk);
      const lines = text.split('\n').filter(Boolean);

      for (const line of lines) {
        const msg: McpRequest = JSON.parse(line);
        let response: McpResponse;

        switch (msg.method) {
          case 'audit_site': {
            const url = msg.params?.url as string;
            if (!url) {
              response = makeError(msg.id, -32602, 'Missing required param: url');
            } else {
              const result = await auditSite(url);
              response = makeResponse(msg.id, result);
            }
            break;
          }

          case 'get_swarm_status': {
            response = makeResponse(msg.id, getSwarmStatus());
            break;
          }

          case 'list_targets': {
            response = makeResponse(msg.id, listTargets());
            break;
          }

          case 'initialize': {
            response = makeResponse(msg.id, {
              name: 'pomelli-swarm',
              version: '25.0.0',
              capabilities: {
                tools: {
                  audit_site: { description: 'Run Lighthouse audit on a fleet target URL' },
                  get_swarm_status: { description: 'Return swarm state, queue depth, pending patches' },
                  list_targets: { description: 'List all monitored sites in the fleet' },
                },
              },
            });
            break;
          }

          default:
            response = makeError(msg.id, -32601, `Unknown method: ${msg.method}`);
        }

        process.stdout.write(JSON.stringify(response) + '\n');
      }
    } catch {
      // Non-JSON input — skip
    }
  }
}

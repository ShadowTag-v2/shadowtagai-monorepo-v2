/**
 * AST-Grep Semantic Scalpel — MCP Server (V25 Pinnacle)
 *
 * Exposes ast-grep search, rewrite, and scan operations over MCP stdio protocol.
 * Replaces regex/sed mutations with deterministic AST-level surgery.
 *
 * Tools exposed:
 *   - ast_search: Find patterns across the codebase using YAML rules
 *   - ast_rewrite: Apply AST-level transformations (fix → rewrite)
 *   - ast_scan: Run all .ast-grep/rules/*.yml and return violations
 */
import { $ } from 'bun';
import { readFileSync, readdirSync, existsSync } from 'fs';
import { join } from 'path';

const WORKSPACE = process.env.WORKSPACE_ROOT
  || '/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball';
const RULES_DIR = join(WORKSPACE, '.ast-grep/rules');

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
 * Search for AST patterns using ast-grep CLI.
 */
async function astSearch(pattern: string, lang: string = 'typescript'): Promise<string> {
  const result = await $`sg run --pattern ${pattern} --lang ${lang} ${WORKSPACE} --json`.quiet().nothrow();
  return result.stdout.toString();
}

/**
 * Apply a rewrite rule: find `pattern`, replace with `rewrite`.
 */
async function astRewrite(
  pattern: string,
  rewrite: string,
  lang: string = 'typescript',
): Promise<string> {
  const result = await $`sg run --pattern ${pattern} --rewrite ${rewrite} --lang ${lang} ${WORKSPACE} --json`.quiet().nothrow();
  return result.stdout.toString();
}

/**
 * Scan the workspace using all YAML rules in .ast-grep/rules/.
 */
async function astScan(): Promise<string> {
  if (!existsSync(RULES_DIR)) {
    return JSON.stringify({ error: 'No rules directory found', path: RULES_DIR });
  }
  const rules = readdirSync(RULES_DIR).filter(f => f.endsWith('.yml') || f.endsWith('.yaml'));
  const result = await $`sg scan --rule ${RULES_DIR} ${WORKSPACE} --json`.quiet().nothrow();
  return JSON.stringify({
    rulesCount: rules.length,
    output: result.stdout.toString(),
    exitCode: result.exitCode,
  });
}

function makeResponse(id: string | number, result: unknown): McpResponse {
  return { jsonrpc: '2.0', id, result };
}

function makeError(id: string | number, code: number, message: string): McpResponse {
  return { jsonrpc: '2.0', id, error: { code, message } };
}

// MCP stdio server bootstrap
if (import.meta.main) {
  console.error('🔬 AST-Grep Semantic Scalpel MCP Server Active (V25 Pinnacle)');
  const decoder = new TextDecoder();

  for await (const chunk of Bun.stdin.stream()) {
    try {
      const text = decoder.decode(chunk);
      const lines = text.split('\n').filter(Boolean);

      for (const line of lines) {
        const msg: McpRequest = JSON.parse(line);
        let response: McpResponse;

        switch (msg.method) {
          case 'ast_search': {
            const pattern = msg.params?.pattern as string;
            const lang = (msg.params?.lang as string) || 'typescript';
            if (!pattern) {
              response = makeError(msg.id, -32602, 'Missing required param: pattern');
            } else {
              const result = await astSearch(pattern, lang);
              response = makeResponse(msg.id, JSON.parse(result || '[]'));
            }
            break;
          }

          case 'ast_rewrite': {
            const pattern = msg.params?.pattern as string;
            const rewrite = msg.params?.rewrite as string;
            const lang = (msg.params?.lang as string) || 'typescript';
            if (!pattern || !rewrite) {
              response = makeError(msg.id, -32602, 'Missing required params: pattern, rewrite');
            } else {
              const result = await astRewrite(pattern, rewrite, lang);
              response = makeResponse(msg.id, JSON.parse(result || '{}'));
            }
            break;
          }

          case 'ast_scan': {
            const result = await astScan();
            response = makeResponse(msg.id, JSON.parse(result));
            break;
          }

          case 'initialize': {
            response = makeResponse(msg.id, {
              name: 'semantic-scalpel',
              version: '25.0.0',
              capabilities: {
                tools: {
                  ast_search: { description: 'Search for AST patterns across the workspace' },
                  ast_rewrite: { description: 'Apply AST-level transformations' },
                  ast_scan: { description: 'Scan with all .ast-grep/rules/*.yml' },
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
      // Non-JSON input or parse error — skip silently
    }
  }
}

/**
 * PNKLN Judge #6 Lite - Cloudflare Worker
 *
 * 3-tier hybrid enforcement at the edge:
 * Tier 1: Rules Engine (<5ms) - 95% of requests
 * Tier 2: Claude via Vertex AI (20-40ms) - 4.5% of requests
 * Tier 3: Reserved for complex PyTorch analysis (future)
 *
 * Target SLA: <50ms p99 latency globally
 * Cost: $0.0029 average per request
 */

// Cloudflare Workers environment
export interface Env {
  GOOGLE_CLOUD_TOKEN: string;
  VERTEX_AI_PROJECT_ID: string;
  VERTEX_AI_REGION: string;
  ANTHROPIC_API_KEY?: string;
}

// Request payload
interface JudgeRequest {
  content: string;
  userId?: string;
  metadata?: Record<string, unknown>;
}

// Response payload
interface JudgeResponse {
  approved: boolean;
  confidence: number;
  reason?: string;
  latencyMs: number;
  cost: number;
  layer: 'rules' | 'claude' | 'pytorch';
  ruleViolations?: Array<{
    rule: string;
    severity: string;
    category: string;
  }>;
}

// ATP 519 Rules (compiled from rules-engine.ts for edge deployment)
const ATP_519_PATTERNS = [
  // Critical violations - instant reject
  {
    pattern: /\b(fraud|scam|ponzi|pyramid scheme|phishing)\b/i,
    rule: 'ATP-519-01',
    severity: 'critical',
    category: 'fraud',
  },
  {
    pattern: /\b(kill|murder|assassinate|bomb|terrorist)\b/i,
    rule: 'ATP-519-10',
    severity: 'critical',
    category: 'violence',
  },
  {
    pattern: /\b(hate speech|racial slur|genocide|lynch)\b/i,
    rule: 'ATP-519-11',
    severity: 'critical',
    category: 'hate',
  },
  {
    pattern: /\b(sell drugs|buy cocaine|meth recipe|heroin)\b/i,
    rule: 'ATP-519-20',
    severity: 'critical',
    category: 'illegal',
  },
  {
    pattern: /\b(child pornography|child abuse|csam)\b/i,
    rule: 'ATP-519-21',
    severity: 'critical',
    category: 'illegal',
  },
  {
    pattern: /\b(human trafficking|sex trafficking)\b/i,
    rule: 'ATP-519-22',
    severity: 'critical',
    category: 'illegal',
  },
  {
    pattern: /\b(steal personal data|data breach|hack database)\b/i,
    rule: 'ATP-519-31',
    severity: 'critical',
    category: 'privacy',
  },
  {
    pattern: /\b(blackmail|extortion|ransom)\b/i,
    rule: 'ATP-519-50',
    severity: 'critical',
    category: 'manipulation',
  },
  {
    pattern: /\b(suicide|kill yourself|self-harm)\b/i,
    rule: 'ATP-519-60',
    severity: 'critical',
    category: 'safety',
  },
  {
    pattern: /\b(build a bomb|make explosives|create poison)\b/i,
    rule: 'ATP-519-61',
    severity: 'critical',
    category: 'safety',
  },

  // High severity - instant reject
  {
    pattern: /\b(money laundering|tax evasion)\b/i,
    rule: 'ATP-519-23',
    severity: 'high',
    category: 'illegal',
  },
  {
    pattern: /\b(dox|doxxing|leak phone number)\b/i,
    rule: 'ATP-519-32',
    severity: 'high',
    category: 'privacy',
  },
  {
    pattern: /\b(manipulate|gaslight|brainwash)\b/i,
    rule: 'ATP-519-51',
    severity: 'high',
    category: 'manipulation',
  },

  // Medium severity - needs analysis
  {
    pattern: /\b(pirated software|cracked version|keygen)\b/i,
    rule: 'ATP-519-40',
    severity: 'medium',
    category: 'ip',
  },
  {
    pattern: /\b(plagiarize|copyright infringement)\b/i,
    rule: 'ATP-519-41',
    severity: 'medium',
    category: 'ip',
  },
  {
    pattern: /\b(fake reviews|review manipulation)\b/i,
    rule: 'ATP-519-71',
    severity: 'medium',
    category: 'spam',
  },
];

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const startTime = Date.now();

    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method === 'GET') {
      return new Response(
        JSON.stringify({
          service: 'PNKLN Judge #6 Lite',
          version: '1.0.0',
          status: 'operational',
          uptime: Date.now(),
        }),
        {
          headers: { 'Content-Type': 'application/json', ...corsHeaders },
        },
      );
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', {
        status: 405,
        headers: corsHeaders,
      });
    }

    try {
      const body: JudgeRequest = await request.json();

      if (!body.content || typeof body.content !== 'string') {
        return new Response(
          JSON.stringify({
            error: 'Missing or invalid "content" field',
          }),
          {
            status: 400,
            headers: { 'Content-Type': 'application/json', ...corsHeaders },
          },
        );
      }

      // TIER 1: Rules Engine (fast path - 95% of requests)
      const rulesResult = enforceRules(body.content);

      if (!rulesResult.needsDeepAnalysis) {
        const response: JudgeResponse = {
          approved: rulesResult.approved,
          confidence: rulesResult.confidence,
          reason: rulesResult.approved
            ? 'No policy violations detected'
            : `Policy violations: ${rulesResult.violations.map((v) => v.rule).join(', ')}`,
          latencyMs: Date.now() - startTime,
          cost: 0.0001, // Rules engine is nearly free
          layer: 'rules',
          ruleViolations: rulesResult.violations,
        };

        return new Response(JSON.stringify(response), {
          headers: {
            'Content-Type': 'application/json',
            'X-Latency-Ms': `${response.latencyMs}`,
            'X-Layer': 'rules',
            ...corsHeaders,
          },
        });
      }

      // TIER 2: Claude via Anthropic API (edge cases - 4.5% of requests)
      // Note: Using Anthropic API directly instead of Vertex AI for edge deployment
      const claudeResult = await analyzeWithClaude(body, env);

      const response: JudgeResponse = {
        ...claudeResult,
        latencyMs: Date.now() - startTime,
        ruleViolations: rulesResult.violations,
      };

      return new Response(JSON.stringify(response), {
        headers: {
          'Content-Type': 'application/json',
          'X-Latency-Ms': `${response.latencyMs}`,
          'X-Layer': 'claude',
          ...corsHeaders,
        },
      });
    } catch (error) {
      console.error('Judge #6 error:', error);

      return new Response(
        JSON.stringify({
          approved: false, // Fail safe
          confidence: 1.0,
          reason: 'Internal error - rejected as safety precaution',
          latencyMs: Date.now() - startTime,
          cost: 0,
          layer: 'error',
          error: error instanceof Error ? error.message : 'Unknown error',
        }),
        {
          status: 500,
          headers: { 'Content-Type': 'application/json', ...corsHeaders },
        },
      );
    }
  },
};

/**
 * Tier 1: Rules Engine Enforcement
 */
function enforceRules(content: string): {
  approved: boolean;
  confidence: number;
  violations: Array<{ rule: string; severity: string; category: string }>;
  needsDeepAnalysis: boolean;
} {
  const violations: Array<{ rule: string; severity: string; category: string }> = [];

  for (const rule of ATP_519_PATTERNS) {
    if (rule.pattern.test(content)) {
      violations.push({
        rule: rule.rule,
        severity: rule.severity,
        category: rule.category,
      });
    }
  }

  const criticalViolations = violations.filter((v) => v.severity === 'critical');
  const highViolations = violations.filter((v) => v.severity === 'high');
  const mediumViolations = violations.filter((v) => v.severity === 'medium');

  if (criticalViolations.length > 0) {
    return {
      approved: false,
      confidence: 1.0,
      violations,
      needsDeepAnalysis: false,
    };
  }

  if (highViolations.length > 0) {
    return {
      approved: false,
      confidence: 0.95,
      violations,
      needsDeepAnalysis: false,
    };
  }

  if (mediumViolations.length > 0) {
    return {
      approved: false,
      confidence: 0.6,
      violations,
      needsDeepAnalysis: true, // Send to Claude for context analysis
    };
  }

  return {
    approved: true,
    confidence: 1.0,
    violations: [],
    needsDeepAnalysis: false,
  };
}

/**
 * Tier 2: Claude Analysis (via Anthropic API)
 */
async function analyzeWithClaude(
  request: JudgeRequest,
  env: Env,
): Promise<Omit<JudgeResponse, 'latencyMs'>> {
  const startTime = Date.now();

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': env.ANTHROPIC_API_KEY || '',
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-5-20250929',
        max_tokens: 512,
        temperature: 0.1,
        system: buildJudgeSystemPrompt(),
        messages: [
          {
            role: 'user',
            content: buildJudgePrompt(request),
          },
        ],
      }),
    });

    if (!response.ok) {
      throw new Error(`Claude API error: ${response.status}`);
    }

    const data = await response.json();
    const decision = parseClaudeDecision(data);

    return {
      ...decision,
      latencyMs: Date.now() - startTime,
      cost: calculateCost(data),
      layer: 'claude',
    };
  } catch (error) {
    console.error('Claude API error:', error);

    // Fallback: reject on error (fail-safe)
    return {
      approved: false,
      confidence: 1.0,
      reason: 'Analysis failed - rejected as safety precaution',
      latencyMs: Date.now() - startTime,
      cost: 0,
      layer: 'claude',
    };
  }
}

function buildJudgeSystemPrompt(): string {
  return `You are PNKLN Judge #6, an AI governance enforcement system.

Your role is to analyze content and determine if it violates policy guidelines.

POLICY FRAMEWORK (ATP 519):
1. No fraud, scams, or deceptive practices
2. No hate speech or incitement to violence
3. No illegal activities or harmful instructions
4. No privacy violations or unauthorized data sharing
5. No intellectual property theft
6. No manipulation or coercion

RESPONSE FORMAT:
You must respond with a JSON object:
{
  "approved": boolean,
  "confidence": number (0-1),
  "reason": "Brief explanation of decision"
}

Be decisive. Err on the side of safety.`;
}

function buildJudgePrompt(request: JudgeRequest): string {
  return `Analyze this content for policy violations:

CONTENT:
${request.content}

USER_ID: ${request.userId || 'anonymous'}

Respond with JSON only.`;
}

function parseClaudeDecision(response: unknown): {
  approved: boolean;
  confidence: number;
  reason?: string;
} {
  try {
    const text = response.content[0].text;
    const jsonMatch = text.match(/\{[\s\S]*\}/);

    if (jsonMatch) {
      const decision = JSON.parse(jsonMatch[0]);
      return {
        approved: decision.approved ?? false,
        confidence: decision.confidence ?? 0.5,
        reason: decision.reason,
      };
    }
  } catch (error) {
    console.error('Failed to parse Claude decision:', error);
  }

  return {
    approved: false,
    confidence: 0.5,
    reason: 'Failed to parse decision',
  };
}

function calculateCost(response: unknown): number {
  // Claude Sonnet 4.5 pricing
  // Input: $3 per 1M tokens
  // Output: $15 per 1M tokens
  const inputTokens = response.usage?.input_tokens || 0;
  const outputTokens = response.usage?.output_tokens || 0;

  const inputCost = (inputTokens / 1_000_000) * 3;
  const outputCost = (outputTokens / 1_000_000) * 15;

  return inputCost + outputCost;
}

/**
 * PNKLN Judge #6 Lite - Cloudflare Workers Edition
 *
 * Revenue-first architecture: Rules Engine → Gemini Flash → PyTorch (escalation only)
 * Target: <50ms p99 latency, $5/month base cost
 */

export interface Env {
  GOOGLE_CLOUD_PROJECT: string;
  GOOGLE_CLOUD_LOCATION: string;
  GOOGLE_CLOUD_TOKEN: string;
  // KV namespace for rate limiting and caching
  JUDGE_KV: KVNamespace;
}

interface JudgeRequest {
  content: string;
  user_id: string;
  context?: Record<string, unknown>;
  require_deep_analysis?: boolean;
}

interface JudgeResponse {
  approved: boolean;
  confidence: number;
  reason?: string;
  latency_ms: number;
  cost_usd: number;
  layer: 'rules' | 'gemini' | 'escalated';
  request_id: string;
}

// ATP 519 violation patterns - compiled at deploy time for performance
const VIOLATION_PATTERNS: Array<{ pattern: RegExp; category: string; severity: number }> = [
  // Financial fraud
  {
    pattern: /\b(ponzi|pyramid\s*scheme|get\s*rich\s*quick)\b/i,
    category: 'financial_fraud',
    severity: 1.0,
  },
  {
    pattern: /\b(guaranteed\s*returns|risk[- ]free\s*investment)\b/i,
    category: 'misleading_claims',
    severity: 0.9,
  },

  // Harmful content
  {
    pattern: /\b(hate\s*speech|racial\s*slur|discriminat)\b/i,
    category: 'hate_speech',
    severity: 1.0,
  },
  {
    pattern: /\b(self[- ]harm|suicide\s*method|how\s*to\s*kill)\b/i,
    category: 'self_harm',
    severity: 1.0,
  },

  // Security violations
  {
    pattern: /\b(hack\s*into|exploit\s*vulnerability|bypass\s*security)\b/i,
    category: 'security_threat',
    severity: 0.95,
  },
  {
    pattern: /\b(steal\s*credentials|phishing\s*attack|malware)\b/i,
    category: 'cyber_attack',
    severity: 1.0,
  },

  // Legal violations
  {
    pattern: /\b(insider\s*trading|money\s*laundering|tax\s*evasion)\b/i,
    category: 'legal_violation',
    severity: 1.0,
  },

  // Misinformation
  {
    pattern: /\b(fake\s*news|election\s*fraud|deep\s*state)\b/i,
    category: 'misinformation',
    severity: 0.8,
  },
];

// Allowed patterns that override violations (context matters)
const ALLOWED_CONTEXTS: RegExp[] = [
  /\b(research|study|educational|academic|preventing|detecting)\b/i,
  /\b(security\s*audit|penetration\s*test|authorized\s*test)\b/i,
];

function generateRequestId(): string {
  return `judge-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function enforceRulesEngine(input: JudgeRequest): {
  needsDeepAnalysis: boolean;
  approved?: boolean;
  reason?: string;
  confidence?: number;
  category?: string;
} {
  const content = input.content.toLowerCase();

  // Check if content is in allowed educational/research context
  const isAllowedContext = ALLOWED_CONTEXTS.some((pattern) => pattern.test(content));

  for (const { pattern, category, severity } of VIOLATION_PATTERNS) {
    if (pattern.test(content)) {
      // If in allowed context and severity < 1.0, escalate to Gemini for nuanced analysis
      if (isAllowedContext && severity < 1.0) {
        return { needsDeepAnalysis: true };
      }

      return {
        needsDeepAnalysis: false,
        approved: false,
        reason: `ATP 519 violation detected: ${category}`,
        confidence: severity,
        category,
      };
    }
  }

  // No violations found by rules engine
  // Short content can pass, longer content needs deeper analysis
  if (content.length < 100) {
    return {
      needsDeepAnalysis: false,
      approved: true,
      confidence: 0.85,
      reason: 'Passed rules engine check',
    };
  }

  return { needsDeepAnalysis: true };
}

async function callGeminiFlash(
  content: string,
  env: Env,
): Promise<{ approved: boolean; confidence: number; reason: string }> {
  const endpoint = `https://${env.GOOGLE_CLOUD_LOCATION}-aiplatform.googleapis.com/v1/projects/${env.GOOGLE_CLOUD_PROJECT}/locations/${env.GOOGLE_CLOUD_LOCATION}/publishers/google/models/gemini-1.5-flash-002:generateContent`;

  const systemPrompt = `You are Judge #6, an AI governance enforcement system. Analyze the following content for policy violations.

Evaluate against these criteria:
1. Financial fraud or misleading investment claims
2. Hate speech or discriminatory content
3. Security threats or hacking instructions
4. Self-harm or dangerous content
5. Legal violations
6. Misinformation or disinformation

Respond in JSON format:
{
  "approved": boolean,
  "confidence": number (0.0-1.0),
  "reason": "brief explanation"
}

Be nuanced: educational/research content about sensitive topics is acceptable. Focus on intent and potential harm.`;

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.GOOGLE_CLOUD_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      contents: [
        {
          role: 'user',
          parts: [{ text: `Analyze this content:\n\n${content}` }],
        },
      ],
      systemInstruction: {
        parts: [{ text: systemPrompt }],
      },
      generationConfig: {
        temperature: 0.1,
        maxOutputTokens: 256,
        responseMimeType: 'application/json',
      },
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Gemini API error: ${response.status} - ${error}`);
  }

  const result = (await response.json()) as {
    candidates: Array<{
      content: {
        parts: Array<{ text: string }>;
      };
    }>;
  };

  const text = result.candidates[0]?.content?.parts[0]?.text || '{}';

  try {
    return JSON.parse(text);
  } catch {
    // Fallback if JSON parsing fails
    return {
      approved: true,
      confidence: 0.5,
      reason: 'Unable to parse Gemini response, defaulting to approved with low confidence',
    };
  }
}

async function rateLimit(userId: string, kv: KVNamespace): Promise<boolean> {
  const key = `ratelimit:${userId}`;
  const current = await kv.get(key);
  const count = current ? parseInt(current, 10) : 0;

  // 100 requests per minute per user
  if (count >= 100) {
    return false;
  }

  await kv.put(key, (count + 1).toString(), { expirationTtl: 60 });
  return true;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const startTime = performance.now();
    const requestId = generateRequestId();

    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Health check
    if (request.method === 'GET' && new URL(request.url).pathname === '/health') {
      return Response.json(
        {
          status: 'healthy',
          version: '1.0.0',
          latency_ms: performance.now() - startTime,
        },
        { headers: corsHeaders },
      );
    }

    // Only accept POST for validation
    if (request.method !== 'POST') {
      return Response.json(
        { error: 'Method not allowed', request_id: requestId },
        { status: 405, headers: corsHeaders },
      );
    }

    try {
      const input: JudgeRequest = await request.json();

      // Validate input
      if (!input.content || !input.user_id) {
        return Response.json(
          { error: 'Missing required fields: content, user_id', request_id: requestId },
          { status: 400, headers: corsHeaders },
        );
      }

      // Rate limiting
      const allowed = await rateLimit(input.user_id, env.JUDGE_KV);
      if (!allowed) {
        return Response.json(
          { error: 'Rate limit exceeded', request_id: requestId },
          { status: 429, headers: corsHeaders },
        );
      }

      // Stage 1: Rules Engine (fast path)
      const rulesResult = enforceRulesEngine(input);

      if (!rulesResult.needsDeepAnalysis && !input.require_deep_analysis) {
        const response: JudgeResponse = {
          approved: rulesResult.approved!,
          confidence: rulesResult.confidence!,
          reason: rulesResult.reason,
          latency_ms: performance.now() - startTime,
          cost_usd: 0.0001,
          layer: 'rules',
          request_id: requestId,
        };

        return Response.json(response, { headers: corsHeaders });
      }

      // Stage 2: Gemini Flash for nuanced analysis
      const geminiResult = await callGeminiFlash(input.content, env);

      const response: JudgeResponse = {
        approved: geminiResult.approved,
        confidence: geminiResult.confidence,
        reason: geminiResult.reason,
        latency_ms: performance.now() - startTime,
        cost_usd: 0.02,
        layer: 'gemini',
        request_id: requestId,
      };

      return Response.json(response, { headers: corsHeaders });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';

      return Response.json(
        {
          error: errorMessage,
          request_id: requestId,
          latency_ms: performance.now() - startTime,
        },
        { status: 500, headers: corsHeaders },
      );
    }
  },
};

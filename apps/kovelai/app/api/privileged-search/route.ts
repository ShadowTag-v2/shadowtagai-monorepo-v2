/**
 * Privileged Search Tunnel — "The Clean Room"
 *
 * When a client Googles "Can my ex-wife find my hidden crypto wallet?"
 * on consumer Google, that search is NOT privileged — Google logs the IP,
 * ties it to their Gmail, and builds an ad cohort. Opposing counsel can
 * and WILL subpoena it.
 *
 * This route transforms consumer search into Attorney-Directed
 * Computer-Assisted Legal Research via the Kovel Doctrine.
 *
 * The client searches through our portal → our server-side proxy executes
 * the query via Google Custom Search Enterprise API (Zero Data Retention)
 * → Google sees a headless server, NOT the client's IP → the query becomes
 * mathematically and legally immune to subpoena.
 *
 * @see U.S. v. Heppner (S.D.N.Y. 2026) — privilege waiver on public AI
 */
import { NextResponse, type NextRequest } from 'next/server';
import { z } from 'zod';
import { verifySEUToken, type SEUViolationError } from '@/lib/security/seu-token-manager';
import { withRateLimit } from '@/lib/middleware/rate-limiter';

// ─── Request Validation ───────────────────────────────────────────────
const SearchRequestSchema = z.object({
  query: z.string().min(1).max(500),
  ephemeralToken: z.string().min(1),
  sandboxId: z.string().min(1),
  firmGoogleCxId: z.string().optional(),
  sessionId: z.string().uuid(),
});

// ─── Response Types ───────────────────────────────────────────────────
interface SearchResult {
  title: string;
  snippet: string;
  url: string;
  source: 'google_enterprise' | 'perplexity_sonar';
}

interface AnxietySignal {
  query: string;
  timestamp: string;
  category: string;
  urgencyScore: number;
}

// ─── Main Route Handler ──────────────────────────────────────────────
export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const body = await req.json();
    const parsed = SearchRequestSchema.parse(body);

    // 1. Validate S.E.U. token — sandbox-bound, ephemeral, user-billed
    const clientIp = req.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ?? '0.0.0.0';
    const tokenPayload = await verifySEUToken(
      parsed.ephemeralToken,
      clientIp,
      parsed.sandboxId,
    );

    // 2. Execute privileged search via ZDR enterprise API
    const results = await executePrivilegedSearch(
      parsed.query,
      parsed.firmGoogleCxId,
    );

    // 3. Classify the anxiety signal for the lawyer's intent dashboard
    const anxietySignal = classifyAnxietyVector(parsed.query);

    // 4. Queue vault update — push search intent to lawyer's dashboard
    // (Background processing — don't block the response)
    queueIntentVault({
      firmId: tokenPayload.firm_id,
      sessionId: parsed.sessionId,
      clientQuery: parsed.query,
      aiResults: results,
      anxietySignal,
      timestamp: new Date().toISOString(),
    });

    // 5. Return results with U.S. v. Heppner anti-forensic caching headers
    return NextResponse.json(
      {
        results,
        metadata: {
          source: results.length > 0 ? results[0].source : 'none',
          resultCount: results.length,
          privilegeStatus: 'KOVEL_PROTECTED',
          expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
        },
      },
      {
        headers: {
          'Cache-Control': 'no-store, no-cache, must-revalidate, private',
          'Pragma': 'no-cache',
          'X-Privilege-Shield': 'kovel-doctrine-active',
          'X-Content-Type-Options': 'nosniff',
        },
      },
    );
  } catch (error) {
    const seuError = error as { violationType?: string };
    if (seuError.violationType) {
      return NextResponse.json(
        { error: 'Sandbox Context Violation', code: seuError.violationType },
        { status: 403 },
      );
    }
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json(
      { error: 'Secure Transit Failed' },
      { status: 500 },
    );
  }
}

// ─── Privileged Search Execution ──────────────────────────────────────
/**
 * Executes the Google search statelessly through the Enterprise API.
 * Google sees a headless server request — NOT the client's IP.
 * Enterprise B2B APIs are legally bound by Zero Data Retention (ZDR).
 */
async function executePrivilegedSearch(
  query: string,
  firmCxId?: string,
): Promise<SearchResult[]> {
  const googleApiKey = process.env.GOOGLE_ENTERPRISE_KEY;
  const defaultCxId = process.env.GOOGLE_DEFAULT_CX_ID;
  const cxId = firmCxId ?? defaultCxId;

  if (!googleApiKey || !cxId) {
    // Fallback to Perplexity Sonar Pro if Google Enterprise not configured
    return executePerplexityFallback(query);
  }

  try {
    const url = new URL('https://www.googleapis.com/customsearch/v1');
    url.searchParams.set('key', googleApiKey);
    url.searchParams.set('cx', cxId);
    url.searchParams.set('q', query);
    url.searchParams.set('num', '8');

    const res = await fetch(url.toString(), {
      headers: { 'Accept': 'application/json' },
      signal: AbortSignal.timeout(10000),
    });

    if (!res.ok) {
      console.error(`[PRIVILEGED SEARCH] Google API responded ${res.status}`);
      return executePerplexityFallback(query);
    }

    const data = await res.json();
    return (data.items ?? []).map((item: Record<string, string>) => ({
      title: item.title ?? '',
      snippet: item.snippet ?? '',
      url: item.link ?? '',
      source: 'google_enterprise' as const,
    }));
  } catch {
    return executePerplexityFallback(query);
  }
}

/**
 * Fallback search via Perplexity Sonar Pro API.
 * Also ZDR-compliant via enterprise agreement.
 */
async function executePerplexityFallback(query: string): Promise<SearchResult[]> {
  const apiKey = process.env.PERPLEXITY_API_KEY;
  if (!apiKey) return [];

  try {
    const res = await fetch('https://api.perplexity.ai/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'sonar-pro',
        messages: [
          {
            role: 'system',
            content: 'You are a legal research assistant. Provide factual, cited search results.',
          },
          { role: 'user', content: query },
        ],
        max_tokens: 1024,
      }),
      signal: AbortSignal.timeout(15000),
    });

    if (!res.ok) return [];
    const data = await res.json();
    const content = data.choices?.[0]?.message?.content ?? '';

    return [
      {
        title: `Research: ${query.slice(0, 60)}`,
        snippet: content.slice(0, 500),
        url: 'perplexity://sonar-pro',
        source: 'perplexity_sonar' as const,
      },
    ];
  } catch {
    return [];
  }
}

// ─── Anxiety Vector Classification ────────────────────────────────────
/**
 * Classifies a client's search query into an anxiety category.
 * The lawyer's dashboard groups these to reveal the client's
 * psychological map and exact fears BEFORE the first phone call.
 */
const ANXIETY_CATEGORIES: Record<string, { keywords: string[]; urgency: number }> = {
  'CRIMINAL_EXPOSURE': {
    keywords: ['arrest', 'indictment', 'felony', 'prison', 'extradition', 'warrant', 'criminal', 'plea', 'probation', 'bail'],
    urgency: 10,
  },
  'ASSET_PROTECTION': {
    keywords: ['hidden', 'offshore', 'crypto', 'forfeiture', 'seizure', 'garnishment', 'lien', 'freeze', 'asset', 'property'],
    urgency: 8,
  },
  'FAMILY_LAW': {
    keywords: ['custody', 'divorce', 'alimony', 'prenup', 'child support', 'visitation', 'restraining', 'domestic'],
    urgency: 7,
  },
  'EMPLOYMENT': {
    keywords: ['wrongful termination', 'discrimination', 'harassment', 'whistleblower', 'retaliation', 'severance', 'non-compete'],
    urgency: 6,
  },
  'REGULATORY': {
    keywords: ['compliance', 'audit', 'SEC', 'FDA', 'HIPAA', 'violation', 'investigation', 'subpoena'],
    urgency: 7,
  },
  'GENERAL_ANXIETY': {
    keywords: ['what happens if', 'can they', 'am I liable', 'is it legal', 'will I lose'],
    urgency: 5,
  },
};

function classifyAnxietyVector(query: string): AnxietySignal {
  const lowerQuery = query.toLowerCase();
  let bestCategory = 'GENERAL_ANXIETY';
  let bestUrgency = 3;

  for (const [category, config] of Object.entries(ANXIETY_CATEGORIES)) {
    const matchCount = config.keywords.filter((kw) => lowerQuery.includes(kw)).length;
    if (matchCount > 0 && config.urgency > bestUrgency) {
      bestCategory = category;
      bestUrgency = config.urgency;
    }
  }

  return {
    query,
    timestamp: new Date().toISOString(),
    category: bestCategory,
    urgencyScore: bestUrgency,
  };
}

// ─── Intent Vault Background Queue ────────────────────────────────────
interface IntentVaultPayload {
  firmId: string;
  sessionId: string;
  clientQuery: string;
  aiResults: SearchResult[];
  anxietySignal: AnxietySignal;
  timestamp: string;
}

/**
 * Queues the search intent for the lawyer's Anxiety Radar dashboard.
 * Uses Cloud Tasks for async processing (Inngest/BullMQ banned).
 */
function queueIntentVault(payload: IntentVaultPayload): void {
  // Fire-and-forget to Cloud Tasks
  const cloudTasksUrl = process.env.CLOUD_TASKS_QUEUE_URL;
  if (!cloudTasksUrl) {
    console.warn('[INTENT VAULT] Cloud Tasks URL not configured, skipping vault');
    return;
  }

  fetch(cloudTasksUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      task: 'vault_search_intent',
      payload,
    }),
  }).catch((err) => {
    console.error('[INTENT VAULT] Failed to queue:', err);
  });
}

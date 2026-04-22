/**
 * Pro Search Intake Loop — Perplexity Paradigm Fold-In
 *
 * Transforms single-shot search queries into multi-step
 * investigative research chains using the Perplexity Pro Search
 * pattern adapted for privileged legal research.
 *
 * Pipeline:
 * 1. Decompose client query into sub-questions (NLP)
 * 2. Execute each sub-question in parallel via ZDR search
 * 3. Synthesize results into structured research brief
 * 4. Generate citation chains with confidence scores
 * 5. Feed synthesis to Oracle Memo pipeline
 *
 * Security: All queries route through the Privileged Search Tunnel.
 * No client IP touches any external search API.
 *
 * @see route.ts — Privileged Search Tunnel (The Clean Room)
 * @see arXiv:2512.14982 — Prompt repetition for accurate decomposition
 */

import { z } from 'zod';

// ─── Schema ──────────────────────────────────────────────────────────

export const ProSearchInputSchema = z.object({
  query: z.string().min(1).max(2000),
  sessionId: z.string().uuid(),
  firmId: z.string().uuid(),
  jurisdiction: z.string().min(2),
  practiceArea: z.string().optional(),
  maxSteps: z.number().int().min(1).max(10).default(5),
});

export type ProSearchInput = z.infer<typeof ProSearchInputSchema>;

export interface ProSearchStep {
  stepNumber: number;
  subQuestion: string;
  searchResults: SearchFragment[];
  synthesized: string;
  confidence: number;
  citations: ProCitation[];
  durationMs: number;
}

export interface SearchFragment {
  title: string;
  snippet: string;
  url: string;
  source: 'google_enterprise' | 'perplexity_sonar' | 'westlaw_stub' | 'lexis_stub';
  relevanceScore: number;
}

export interface ProCitation {
  index: number;
  authority: string;
  type: 'statute' | 'case' | 'regulation' | 'rule' | 'secondary' | 'web';
  excerpt: string;
  url: string;
  confidence: number;
}

export interface ProSearchResult {
  sessionId: string;
  originalQuery: string;
  steps: ProSearchStep[];
  finalSynthesis: string;
  allCitations: ProCitation[];
  totalDurationMs: number;
  privilegeStatus: 'KOVEL_PROTECTED';
}

// ─── Query Decomposition ─────────────────────────────────────────────

/**
 * Decomposes a complex legal query into atomic sub-questions.
 *
 * Uses arXiv:2512.14982 prompt repetition for non-reasoning tiers.
 * Example: "Can my employer fire me for whistleblowing in California?"
 * → ["What are California whistleblower protections?",
 *    "What constitutes protected whistleblowing activity under Cal. Lab. Code?",
 *    "What damages are available for wrongful termination - whistleblower retaliation?",
 *    "What is the statute of limitations for whistleblower claims in CA?",
 *    "Recent California whistleblower case law 2024-2025"]
 */
export function decomposeQuery(
  query: string,
  jurisdiction: string,
  maxSteps: number,
): string[] {
  // Static decomposition heuristics (LLM decomposition happens server-side)
  const subQuestions: string[] = [];
  const queryLower = query.toLowerCase();

  // Always include the original query as step 1
  subQuestions.push(query);

  // Jurisdiction-specific expansion
  if (jurisdiction) {
    subQuestions.push(`${query} ${jurisdiction} law`);
  }

  // Statute of limitations is always relevant
  if (queryLower.includes('sue') || queryLower.includes('claim') || queryLower.includes('file')) {
    subQuestions.push(`Statute of limitations ${query} ${jurisdiction}`);
  }

  // Damages query
  subQuestions.push(`What damages are available for ${query} ${jurisdiction}`);

  // Recent case law
  subQuestions.push(`Recent case law ${query} ${jurisdiction} 2024 2025`);

  return subQuestions.slice(0, maxSteps);
}

// ─── Pro Search Executor ─────────────────────────────────────────────

/**
 * Executes the full Pro Search intake loop.
 *
 * Each step:
 * 1. Takes a sub-question from the decomposition
 * 2. Calls the Privileged Search Tunnel (/api/privileged-search)
 * 3. Synthesizes results into structured brief fragment
 * 4. Extracts citations from the results
 * 5. Feeds context to the next step for progressive refinement
 *
 * @param input - The pro search input
 * @param searchFn - Injectable search function (for testing)
 */
export async function executeProSearch(
  input: ProSearchInput,
  searchFn?: (query: string) => Promise<SearchFragment[]>,
): Promise<ProSearchResult> {
  const startTime = Date.now();
  const subQuestions = decomposeQuery(input.query, input.jurisdiction, input.maxSteps);
  const steps: ProSearchStep[] = [];
  const allCitations: ProCitation[] = [];
  let citationIndex = 1;

  for (let i = 0; i < subQuestions.length; i++) {
    const stepStart = Date.now();
    const subQuestion = subQuestions[i];

    // Execute search with progressive context
    const contextPrefix = steps.length > 0
      ? `[Context from previous research: ${steps.map(s => s.synthesized).join(' | ')}]\n\n`
      : '';

    const enrichedQuery = contextPrefix + subQuestion;
    let searchResults: SearchFragment[];

    if (searchFn) {
      searchResults = await searchFn(enrichedQuery);
    } else {
      searchResults = await callPrivilegedSearchAPI(enrichedQuery, input.sessionId, input.firmId);
    }

    // Score relevance
    const scoredResults = searchResults.map((r) => ({
      ...r,
      relevanceScore: scoreRelevance(r, input.query),
    }));

    // Extract citations from results
    const stepCitations: ProCitation[] = scoredResults
      .filter((r) => r.relevanceScore > 0.3)
      .map((r) => ({
        index: citationIndex++,
        authority: r.title,
        type: classifyCitationType(r),
        excerpt: r.snippet.slice(0, 300),
        url: r.url,
        confidence: r.relevanceScore,
      }));

    allCitations.push(...stepCitations);

    // Synthesize this step
    const synthesized = synthesizeStep(subQuestion, scoredResults);

    steps.push({
      stepNumber: i + 1,
      subQuestion,
      searchResults: scoredResults,
      synthesized,
      confidence: scoredResults.length > 0
        ? scoredResults.reduce((sum, r) => sum + r.relevanceScore, 0) / scoredResults.length
        : 0,
      citations: stepCitations,
      durationMs: Date.now() - stepStart,
    });
  }

  // Final synthesis across all steps
  const finalSynthesis = synthesizeFinal(input.query, steps);

  return {
    sessionId: input.sessionId,
    originalQuery: input.query,
    steps,
    finalSynthesis,
    allCitations,
    totalDurationMs: Date.now() - startTime,
    privilegeStatus: 'KOVEL_PROTECTED',
  };
}

// ─── Internal Helpers ────────────────────────────────────────────────

function scoreRelevance(result: SearchFragment, originalQuery: string): number {
  const queryTerms = originalQuery.toLowerCase().split(/\s+/);
  const combinedText = `${result.title} ${result.snippet}`.toLowerCase();
  const matches = queryTerms.filter((term) => combinedText.includes(term)).length;
  return Math.min(1, matches / Math.max(queryTerms.length, 1));
}

function classifyCitationType(
  result: SearchFragment,
): ProCitation['type'] {
  const text = `${result.title} ${result.url}`.toLowerCase();
  if (text.includes('code') || text.includes('statute') || text.includes('§')) return 'statute';
  if (text.includes('v.') || text.includes('case') || text.includes('court')) return 'case';
  if (text.includes('reg') || text.includes('cfr')) return 'regulation';
  if (text.includes('rule')) return 'rule';
  if (text.includes('law review') || text.includes('article')) return 'secondary';
  return 'web';
}

function synthesizeStep(subQuestion: string, results: SearchFragment[]): string {
  if (results.length === 0) return `No results found for: ${subQuestion}`;
  const topSnippets = results.slice(0, 3).map((r) => r.snippet).join(' ');
  return `[${subQuestion}]: ${topSnippets}`;
}

function synthesizeFinal(originalQuery: string, steps: ProSearchStep[]): string {
  const stepSummaries = steps.map((s) => `Step ${s.stepNumber}: ${s.synthesized}`).join('\n');
  return `# Pro Search Research Brief\n\n**Query:** ${originalQuery}\n\n## Research Steps\n${stepSummaries}\n\n## Total Citations: ${steps.reduce((sum, s) => sum + s.citations.length, 0)}`;
}

async function callPrivilegedSearchAPI(
  query: string,
  sessionId: string,
  firmId: string,
): Promise<SearchFragment[]> {
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL ?? 'http://localhost:3000';
  try {
    const res = await fetch(`${baseUrl}/api/privileged-search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        ephemeralToken: 'internal-pro-search',
        sandboxId: 'pro-search-sandbox',
        sessionId,
      }),
      signal: AbortSignal.timeout(15000),
    });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.results ?? []).map((r: Record<string, string>) => ({
      ...r,
      relevanceScore: 0.5,
    }));
  } catch {
    return [];
  }
}

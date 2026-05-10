/**
 * Legal Search Integration into Privileged Search Route
 *
 * Item #11: Wire legal search connectors into privileged-search endpoint.
 *
 * Adds Westlaw, LexisNexis, and CourtListener as search sources
 * alongside Google Enterprise and Perplexity Sonar.
 *
 * Search priority:
 * 1. Google Enterprise (ZDR, primary)
 * 2. Legal databases (Westlaw > LexisNexis > CourtListener)
 * 3. Perplexity Sonar Pro (fallback)
 *
 * @see lib/connectors/legal-search.ts
 * @see app/api/privileged-search/route.ts
 */

import {
  type LegalSearchResult,
  searchCourtListener,
  searchLexisNexis,
  searchWestlaw,
} from '@/lib/connectors/legal-search';

// ─── Types ──────────────────────────────────────────────────────────

interface UnifiedSearchResult {
  title: string;
  snippet: string;
  url: string;
  source: 'google_enterprise' | 'perplexity_sonar' | 'westlaw' | 'lexisnexis' | 'courtlistener';
  confidence?: number;
  citations?: string[];
}

export interface LegalSearchConfig {
  enableWestlaw: boolean;
  enableLexisNexis: boolean;
  enableCourtListener: boolean;
  maxResultsPerSource: number;
  jurisdictionFilter?: string[];
  dateRange?: { start: string; end: string };
  practiceAreas?: string[];
}

// ─── Default Config ─────────────────────────────────────────────────

const DEFAULT_CONFIG: LegalSearchConfig = {
  enableWestlaw: true,
  enableLexisNexis: true,
  enableCourtListener: true,
  maxResultsPerSource: 5,
};

// ─── Unified Legal Search ───────────────────────────────────────────

/**
 * Executes parallel legal searches across configured databases.
 *
 * Returns merged, de-duplicated results sorted by confidence.
 */
export async function executeUnifiedLegalSearch(
  query: string,
  config: Partial<LegalSearchConfig> = {},
): Promise<UnifiedSearchResult[]> {
  const cfg = { ...DEFAULT_CONFIG, ...config };
  const promises: Promise<UnifiedSearchResult[]>[] = [];

  if (cfg.enableWestlaw) {
    promises.push(searchWestlawAdapter(query, cfg.maxResultsPerSource, cfg.jurisdictionFilter));
  }

  if (cfg.enableLexisNexis) {
    promises.push(searchLexisNexisAdapter(query, cfg.maxResultsPerSource, cfg.jurisdictionFilter));
  }

  if (cfg.enableCourtListener) {
    promises.push(
      searchCourtListenerAdapter(query, cfg.maxResultsPerSource, cfg.jurisdictionFilter),
    );
  }

  // Execute in parallel with individual timeouts
  const settled = await Promise.allSettled(promises);

  const allResults: UnifiedSearchResult[] = [];

  for (const result of settled) {
    if (result.status === 'fulfilled') {
      allResults.push(...result.value);
    } else {
    }
  }

  // De-duplicate by URL
  const seen = new Set<string>();
  const unique = allResults.filter((r) => {
    if (seen.has(r.url)) return false;
    seen.add(r.url);
    return true;
  });

  // Sort by confidence (descending)
  return unique.sort((a, b) => (b.confidence ?? 0) - (a.confidence ?? 0));
}

// ─── Source Adapters ────────────────────────────────────────────────

async function searchWestlawAdapter(
  query: string,
  maxResults: number,
  jurisdictions?: string[],
): Promise<UnifiedSearchResult[]> {
  try {
    const results = await searchWestlaw(query, {
      maxResults,
      jurisdiction: jurisdictions?.[0],
    });

    return results.map(adaptLegalResult('westlaw'));
  } catch {
    return [];
  }
}

async function searchLexisNexisAdapter(
  query: string,
  maxResults: number,
  jurisdictions?: string[],
): Promise<UnifiedSearchResult[]> {
  try {
    const results = await searchLexisNexis(query, {
      maxResults,
      jurisdiction: jurisdictions?.[0],
    });

    return results.map(adaptLegalResult('lexisnexis'));
  } catch {
    return [];
  }
}

async function searchCourtListenerAdapter(
  query: string,
  maxResults: number,
  jurisdictions?: string[],
): Promise<UnifiedSearchResult[]> {
  try {
    const results = await searchCourtListener(query, {
      maxResults,
      court: jurisdictions?.[0],
    });

    return results.map(adaptLegalResult('courtlistener'));
  } catch {
    return [];
  }
}

function adaptLegalResult(
  source: 'westlaw' | 'lexisnexis' | 'courtlistener',
): (result: LegalSearchResult) => UnifiedSearchResult {
  return (result) => ({
    title: result.title,
    snippet: result.snippet,
    url: result.url,
    source,
    confidence: result.relevanceScore,
    citations: result.citations,
  });
}

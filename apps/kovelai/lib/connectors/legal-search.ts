/**
 * Legal Research API Connector
 *
 * Sprint Item #15: Westlaw/LexisNexis API integration layer.
 *
 * Provides a unified interface for querying legal databases:
 * - Westlaw (via Thomson Reuters API)
 * - LexisNexis (via LexisNexis API)
 * - Google Scholar (fallback, free)
 * - CourtListener (RECAP/PACER, free)
 *
 * Each connector implements the LegalSearchProvider interface.
 * The router picks the best source based on firm configuration.
 *
 * @see lib/auth/seu-token.ts — Firm-scoped access
 */

import { z } from 'zod';

// ─── Unified Types ──────────────────────────────────────────────────

export const LegalCitationSchema = z.object({
  caseId: z.string(),
  caseName: z.string(),
  citation: z.string(), // e.g., "296 F.2d 918 (2d Cir. 1961)"
  court: z.string(),
  dateDecided: z.string(),
  snippet: z.string(),
  url: z.string().url().optional(),
  source: z.enum(['westlaw', 'lexisnexis', 'google_scholar', 'courtlistener']),
  relevanceScore: z.number().min(0).max(1),
});

export type LegalCitation = z.infer<typeof LegalCitationSchema>;

export interface LegalSearchQuery {
  query: string;
  jurisdiction?: string;
  dateRange?: { start: string; end: string };
  courtLevel?: 'supreme' | 'circuit' | 'district' | 'state' | 'all';
  maxResults?: number;
}

export interface LegalSearchResult {
  citations: LegalCitation[];
  totalResults: number;
  searchTime: number;
  provider: string;
}

// ─── Provider Interface ─────────────────────────────────────────────

interface LegalSearchProvider {
  name: string;
  search(query: LegalSearchQuery, apiKey: string): Promise<LegalSearchResult>;
  isAvailable(): boolean;
}

// ─── Westlaw Connector ──────────────────────────────────────────────

class WestlawConnector implements LegalSearchProvider {
  name = 'westlaw';
  private baseUrl = 'https://api.thomsonreuters.com/westlaw/v1';

  async search(query: LegalSearchQuery, apiKey: string): Promise<LegalSearchResult> {
    const start = performance.now();

    const params = new URLSearchParams({
      query: query.query,
      maxResults: String(query.maxResults ?? 10),
      ...(query.jurisdiction && { jurisdiction: query.jurisdiction }),
      ...(query.courtLevel && { courtLevel: query.courtLevel }),
    });

    const response = await fetch(`${this.baseUrl}/search?${params}`, {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'X-Client-Id': 'kovelai-privileged-search',
      },
    });

    if (!response.ok) {
      throw new Error(`Westlaw API error: ${response.status}`);
    }

    const data = await response.json();
    const searchTime = Math.round(performance.now() - start);

    return {
      citations: (data.results || []).map((r: Record<string, unknown>) => ({
        caseId: r.id as string,
        caseName: r.title as string,
        citation: r.citation as string,
        court: r.court as string,
        dateDecided: r.date as string,
        snippet: r.snippet as string,
        url: r.url as string,
        source: 'westlaw' as const,
        relevanceScore: (r.score as number) ?? 0.5,
      })),
      totalResults: data.totalResults ?? 0,
      searchTime,
      provider: 'westlaw',
    };
  }

  isAvailable(): boolean {
    return !!process.env.WESTLAW_API_KEY;
  }
}

// ─── LexisNexis Connector ───────────────────────────────────────────

class LexisNexisConnector implements LegalSearchProvider {
  name = 'lexisnexis';
  private baseUrl = 'https://api.lexisnexis.com/v1';

  async search(query: LegalSearchQuery, apiKey: string): Promise<LegalSearchResult> {
    const start = performance.now();

    const response = await fetch(`${this.baseUrl}/search`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query.query,
        sources: ['cases'],
        jurisdiction: query.jurisdiction,
        maxResults: query.maxResults ?? 10,
      }),
    });

    if (!response.ok) {
      throw new Error(`LexisNexis API error: ${response.status}`);
    }

    const data = await response.json();
    const searchTime = Math.round(performance.now() - start);

    return {
      citations: (data.documents || []).map((d: Record<string, unknown>) => ({
        caseId: d.id as string,
        caseName: d.title as string,
        citation: d.citation as string,
        court: d.court as string,
        dateDecided: d.dateDecided as string,
        snippet: d.excerpt as string,
        url: d.url as string,
        source: 'lexisnexis' as const,
        relevanceScore: (d.relevance as number) ?? 0.5,
      })),
      totalResults: data.total ?? 0,
      searchTime,
      provider: 'lexisnexis',
    };
  }

  isAvailable(): boolean {
    return !!process.env.LEXISNEXIS_API_KEY;
  }
}

// ─── CourtListener Connector (Free/RECAP) ───────────────────────────

class CourtListenerConnector implements LegalSearchProvider {
  name = 'courtlistener';
  private baseUrl = 'https://www.courtlistener.com/api/rest/v4';

  async search(query: LegalSearchQuery, _apiKey: string): Promise<LegalSearchResult> {
    const start = performance.now();

    const params = new URLSearchParams({
      q: query.query,
      type: 'o', // opinions
      order_by: 'score desc',
      ...(query.maxResults && { page_size: String(Math.min(query.maxResults, 20)) }),
    });

    const response = await fetch(`${this.baseUrl}/search/?${params}`, {
      headers: {
        'Authorization': `Token ${process.env.COURTLISTENER_API_KEY ?? ''}`,
      },
    });

    if (!response.ok) {
      throw new Error(`CourtListener API error: ${response.status}`);
    }

    const data = await response.json();
    const searchTime = Math.round(performance.now() - start);

    return {
      citations: (data.results || []).map((r: Record<string, unknown>) => ({
        caseId: String(r.id),
        caseName: r.caseName as string ?? 'Untitled',
        citation: r.citation as string ?? '',
        court: r.court as string ?? '',
        dateDecided: r.dateFiled as string ?? '',
        snippet: (r.snippet as string ?? '').slice(0, 300),
        url: `https://www.courtlistener.com${r.absolute_url as string ?? ''}`,
        source: 'courtlistener' as const,
        relevanceScore: 0.5,
      })),
      totalResults: data.count ?? 0,
      searchTime,
      provider: 'courtlistener',
    };
  }

  isAvailable(): boolean {
    return true; // Always available (rate limited)
  }
}

// ─── Router ─────────────────────────────────────────────────────────

const providers: LegalSearchProvider[] = [
  new WestlawConnector(),
  new LexisNexisConnector(),
  new CourtListenerConnector(),
];

/**
 * Routes a legal search to the best available provider.
 * Priority: Westlaw > LexisNexis > CourtListener
 */
export async function searchLegalDatabases(
  query: LegalSearchQuery,
  preferredProvider?: string,
  firmApiKeys?: Record<string, string>,
): Promise<LegalSearchResult> {
  // If firm has BYOK keys, use those
  const effectiveKeys = firmApiKeys ?? {};

  // Find the preferred or best available provider
  let provider: LegalSearchProvider | undefined;

  if (preferredProvider) {
    provider = providers.find((p) => p.name === preferredProvider);
  }

  if (!provider) {
    provider = providers.find((p) => p.isAvailable());
  }

  if (!provider) {
    throw new Error('No legal search provider available');
  }

  const apiKey = effectiveKeys[provider.name] ?? process.env[`${provider.name.toUpperCase()}_API_KEY`] ?? '';

  return provider.search(query, apiKey);
}

/**
 * Returns the list of available providers for a firm.
 */
export function getAvailableProviders(): string[] {
  return providers.filter((p) => p.isAvailable()).map((p) => p.name);
}

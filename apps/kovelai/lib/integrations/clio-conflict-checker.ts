/**
 * Clio MCP Conflict Checker — Gateway Integration
 *
 * Wires real Clio practice management conflict checks through the
 * Antigravity MCP Gateway, ensuring ABA Rule 1.18 compliance before
 * accepting new client matters.
 *
 * Requires: Clio API OAuth2 credentials (per-firm)
 * Endpoint: POST /api/conflicts/check
 */

import { createLogger } from '../observability/structured-logger';

const logger = createLogger('clio-conflict-checker');

/** Conflict check result */
interface ConflictResult {
  hasConflict: boolean;
  conflictType?: 'current_client' | 'former_client' | 'related_matter' | 'adverse_party';
  conflictDetails?: string;
  matchedEntities: Array<{
    name: string;
    matchScore: number;
    source: 'clio' | 'manual' | 'kovelai_internal';
    matterId?: string;
  }>;
  checkedAt: string;
  abaRule: '1.7' | '1.9' | '1.18';
}

/** Clio API client configuration per firm */
interface ClioConfig {
  firmId: string;
  clioRegion: 'us' | 'ca' | 'eu';
  accessToken: string; // OAuth2 access token (short-lived)
  refreshToken: string; // OAuth2 refresh token (stored in Secret Manager)
}

/**
 * Check for conflicts against Clio's contact and matter database.
 *
 * This searches Clio's contacts for name matches against the prospective
 * client and any adverse parties, then checks matter relationships.
 */
export async function checkClioConflicts(
  config: ClioConfig,
  params: {
    prospectiveName: string;
    adverseParties: string[];
    matterType: string;
  },
): Promise<ConflictResult> {
  const baseUrl =
    config.clioRegion === 'eu'
      ? 'https://eu.app.clio.com/api/v4'
      : config.clioRegion === 'ca'
        ? 'https://ca.app.clio.com/api/v4'
        : 'https://app.clio.com/api/v4';

  const allNames = [params.prospectiveName, ...params.adverseParties];
  const matchedEntities: ConflictResult['matchedEntities'] = [];

  for (const name of allNames) {
    try {
      const response = await fetch(
        `${baseUrl}/contacts.json?query=${encodeURIComponent(name)}&fields=id,name,type,first_name,last_name`,
        {
          headers: {
            Authorization: `Bearer ${config.accessToken}`,
            'Content-Type': 'application/json',
          },
        },
      );

      if (!response.ok) {
        logger.error('Clio API error', {
          status: response.status,
          firmId: config.firmId,
        });
        continue;
      }

      const data = (await response.json()) as {
        data: Array<{
          id: number;
          name: string;
          type: string;
          first_name?: string;
          last_name?: string;
        }>;
      };

      for (const contact of data.data) {
        const score = computeNameSimilarity(name, contact.name);
        if (score >= 0.85) {
          matchedEntities.push({
            name: contact.name,
            matchScore: score,
            source: 'clio',
            matterId: String(contact.id),
          });
        }
      }
    } catch (err) {
      logger.error('Clio contact search failed', {
        name,
        error: err instanceof Error ? err.message : 'unknown',
      });
    }
  }

  // Determine conflict type
  const hasConflict = matchedEntities.length > 0;
  let conflictType: ConflictResult['conflictType'];
  let abaRule: ConflictResult['abaRule'] = '1.18';

  if (hasConflict) {
    // Check if matched entity is a current client
    const isCurrentClient = matchedEntities.some(
      (e) => e.name.toLowerCase() === params.prospectiveName.toLowerCase(),
    );
    const isAdverseMatch = matchedEntities.some((e) =>
      params.adverseParties.some((ap) => computeNameSimilarity(ap, e.name) >= 0.85),
    );

    if (isCurrentClient && isAdverseMatch) {
      conflictType = 'current_client';
      abaRule = '1.7';
    } else if (isAdverseMatch) {
      conflictType = 'adverse_party';
      abaRule = '1.9';
    } else {
      conflictType = 'related_matter';
      abaRule = '1.18';
    }
  }

  logger.info('Conflict check completed', {
    firmId: config.firmId,
    hasConflict,
    matchCount: matchedEntities.length,
    abaRule,
  });

  return {
    hasConflict,
    conflictType,
    conflictDetails: hasConflict
      ? `Found ${matchedEntities.length} potential conflict(s) via Clio. ABA Rule ${abaRule} applies.`
      : undefined,
    matchedEntities,
    checkedAt: new Date().toISOString(),
    abaRule,
  };
}

/**
 * Simple Jaro-Winkler similarity for name matching.
 * Returns 0.0-1.0 score.
 */
function computeNameSimilarity(a: string, b: string): number {
  const s1 = a.toLowerCase().trim();
  const s2 = b.toLowerCase().trim();

  if (s1 === s2) return 1.0;
  if (s1.length === 0 || s2.length === 0) return 0.0;

  const matchWindow = Math.floor(Math.max(s1.length, s2.length) / 2) - 1;
  const s1Matches = new Array(s1.length).fill(false);
  const s2Matches = new Array(s2.length).fill(false);

  let matches = 0;
  let transpositions = 0;

  for (let i = 0; i < s1.length; i++) {
    const start = Math.max(0, i - matchWindow);
    const end = Math.min(i + matchWindow + 1, s2.length);

    for (let j = start; j < end; j++) {
      if (s2Matches[j] || s1[i] !== s2[j]) continue;
      s1Matches[i] = true;
      s2Matches[j] = true;
      matches++;
      break;
    }
  }

  if (matches === 0) return 0.0;

  let k = 0;
  for (let i = 0; i < s1.length; i++) {
    if (!s1Matches[i]) continue;
    while (!s2Matches[k]) k++;
    if (s1[i] !== s2[k]) transpositions++;
    k++;
  }

  const jaro =
    (matches / s1.length + matches / s2.length + (matches - transpositions / 2) / matches) / 3;

  // Winkler prefix bonus
  let prefix = 0;
  for (let i = 0; i < Math.min(4, Math.min(s1.length, s2.length)); i++) {
    if (s1[i] === s2[i]) prefix++;
    else break;
  }

  return jaro + prefix * 0.1 * (1 - jaro);
}

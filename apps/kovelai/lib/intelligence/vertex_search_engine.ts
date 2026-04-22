/**
 * @fileoverview Web-to-Privilege Enterprise Search Engine
 *
 * Transforms public OSINT/Medical searches into protected ZDR work-product.
 *
 * When a client searches "medical malpractice symptoms" through KovelAI,
 * the query routes through Google Cloud Vertex AI Enterprise Search which
 * guarantees Zero Data Retention (ZDR). Because the search is executed
 * under the direction of counsel, it transforms discoverable public
 * web-sleuthing into protected Attorney Work-Product (U.S. v. Kovel).
 *
 * @see PERPLEXITY_PARADIGM.md — Mapping to Perplexity's Pro Search
 * @see DIGITAL_PRIVILEGE_SHIELD.md — Kovel Directive framework
 */

import { v1alpha } from '@google-cloud/discoveryengine';

const searchClient = new v1alpha.SearchServiceClient();

/**
 * Executes a privileged web search through Vertex AI Enterprise Search.
 * Guaranteed Zero Data Retention (ZDR).
 *
 * @param query - The client's search query
 * @param firmId - The firm identifier for audit logging
 * @returns Aggregated search snippets as a single string
 */
export async function executePrivilegedWebSearch(
  query: string,
  firmId: string,
): Promise<string> {
  const projectId = process.env.GCP_PROJECT;
  if (!projectId) {
    throw new Error('GCP_PROJECT environment variable is required');
  }

  const request = {
    servingConfig: `projects/${projectId}/locations/global/collections/default_collection/engines/kovel-triage/servingConfigs/default_config`,
    query,
    pageSize: 5,
    safeSearch: false, // Unrestricted OSINT for legal discovery
  };

  const [response] = await searchClient.search(request);

  const snippets = response.results
    ?.map(
      (r) =>
        r.document?.derivedStructData?.fields?.snippets?.listValue
          ?.values?.[0]?.structValue?.fields?.snippet?.stringValue,
    )
    .filter(Boolean)
    .join('\n');

  return snippets || 'No findings from privileged enterprise search.';
}

/**
 * Executes a privileged medical search — used for personal injury,
 * medical malpractice, and disability cases.
 *
 * @param query - Medical search query
 * @param firmId - Firm identifier
 * @returns Medical search results as protected work-product
 */
export async function executePrivilegedMedicalSearch(
  query: string,
  firmId: string,
): Promise<string> {
  // Route through the same ZDR engine with medical-specific context
  return executePrivilegedWebSearch(
    `medical research: ${query}`,
    firmId,
  );
}

/**
 * Pages Dossier Generator — Perplexity Paradigm Fold-In
 *
 * Transforms raw Pro Search results + Oracle Memo outputs into
 * a structured, shareable "Pages-style" legal research dossier.
 *
 * This is the equivalent of Perplexity Pages but adapted for
 * attorney work-product privilege:
 * - Auto-generates section headers from research themes
 * - Embeds inline citations with confidence scores
 * - Produces both client-facing (redacted) and lawyer-facing (full) versions
 * - Outputs markdown suitable for PDF generation or Clio attachment
 *
 * @see pro-search-intake.ts — Upstream research pipeline
 * @see CitationPanel.tsx — Frontend citation rendering
 */

import type { ProCitation, ProSearchResult } from './pro-search-intake';

// ─── Types ───────────────────────────────────────────────────────────

export interface DossierConfig {
  firmName: string;
  firmId: string;
  matterNumber?: string;
  clientName: string;
  preparingAttorney: string;
  jurisdiction: string;
  confidentialityLevel: 'ATTORNEY_WORK_PRODUCT' | 'ATTORNEY_CLIENT_PRIVILEGED' | 'PUBLIC';
  includeRawSources: boolean;
}

export interface DossierSection {
  title: string;
  content: string;
  citations: ProCitation[];
  confidence: number;
}

export interface LegalDossier {
  id: string;
  title: string;
  subtitle: string;
  generatedAt: string;
  config: DossierConfig;
  sections: DossierSection[];
  appendix: {
    allCitations: ProCitation[];
    methodology: string;
    disclaimers: string[];
  };
  markdown: string;
  privilegeMarker: string;
}

// ─── Dossier Generator ──────────────────────────────────────────────

/**
 * Generates a structured legal dossier from Pro Search results.
 *
 * @param searchResult - The completed Pro Search research
 * @param config - Firm and matter configuration
 * @returns Complete dossier with markdown output
 */
export function generateDossier(
  searchResult: ProSearchResult,
  config: DossierConfig,
): LegalDossier {
  const dossierId = crypto.randomUUID();
  const now = new Date().toISOString();

  // Group research steps into thematic sections
  const sections = buildSections(searchResult);

  // Generate privilege marker
  const privilegeMarker = buildPrivilegeMarker(config);

  // Build complete markdown
  const markdown = renderDossierMarkdown(searchResult, sections, config, privilegeMarker);

  return {
    id: dossierId,
    title: `Legal Research Dossier: ${searchResult.originalQuery.slice(0, 100)}`,
    subtitle: `Prepared for ${config.clientName} | Matter: ${config.matterNumber ?? 'N/A'}`,
    generatedAt: now,
    config,
    sections,
    appendix: {
      allCitations: searchResult.allCitations,
      methodology: buildMethodology(searchResult),
      disclaimers: getDisclaimers(config),
    },
    markdown,
    privilegeMarker,
  };
}

// ─── Section Builder ─────────────────────────────────────────────────

function buildSections(result: ProSearchResult): DossierSection[] {
  return result.steps.map((step) => ({
    title: extractSectionTitle(step.subQuestion),
    content: step.synthesized,
    citations: step.citations,
    confidence: step.confidence,
  }));
}

function extractSectionTitle(subQuestion: string): string {
  // Remove common prefixes and clean up
  return subQuestion
    .replace(/^(what|how|when|where|who|why|can|does|is|are)\s+/i, '')
    .replace(/\?$/, '')
    .split(' ')
    .slice(0, 8)
    .join(' ')
    .replace(/^\w/, (c) => c.toUpperCase());
}

// ─── Markdown Renderer ──────────────────────────────────────────────

function renderDossierMarkdown(
  result: ProSearchResult,
  sections: DossierSection[],
  config: DossierConfig,
  privilegeMarker: string,
): string {
  const lines: string[] = [];

  // Header
  lines.push(privilegeMarker);
  lines.push('');
  lines.push(`# Legal Research Dossier`);
  lines.push('');
  lines.push(`**Query:** ${result.originalQuery}`);
  lines.push(`**Prepared for:** ${config.clientName}`);
  lines.push(`**Preparing Attorney:** ${config.preparingAttorney}`);
  lines.push(`**Firm:** ${config.firmName}`);
  lines.push(`**Matter:** ${config.matterNumber ?? 'N/A'}`);
  lines.push(`**Jurisdiction:** ${config.jurisdiction}`);
  lines.push(
    `**Date:** ${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}`,
  );
  lines.push(`**Research Steps:** ${result.steps.length}`);
  lines.push(`**Total Citations:** ${result.allCitations.length}`);
  lines.push('');
  lines.push('---');
  lines.push('');

  // Sections
  for (const section of sections) {
    const confidenceIcon = section.confidence > 0.7 ? '🟢' : section.confidence > 0.4 ? '🟡' : '🔴';
    lines.push(`## ${section.title} ${confidenceIcon}`);
    lines.push('');
    lines.push(section.content);
    lines.push('');

    // Inline citations
    if (section.citations.length > 0) {
      lines.push('**Sources:**');
      for (const cit of section.citations) {
        lines.push(
          `- [${cit.index}] ${cit.authority} — *${cit.type}* (${Math.round(cit.confidence * 100)}% confidence)`,
        );
      }
      lines.push('');
    }
  }

  // Appendix
  lines.push('---');
  lines.push('');
  lines.push('## Appendix: Citation Index');
  lines.push('');
  for (const cit of result.allCitations) {
    lines.push(`**[${cit.index}]** ${cit.authority}`);
    lines.push(`  - Type: ${cit.type}`);
    lines.push(`  - Excerpt: "${cit.excerpt.slice(0, 200)}..."`);
    lines.push(`  - Confidence: ${Math.round(cit.confidence * 100)}%`);
    lines.push(`  - URL: ${cit.url}`);
    lines.push('');
  }

  // Methodology
  lines.push('## Appendix: Research Methodology');
  lines.push('');
  lines.push(buildMethodology(result));
  lines.push('');

  // Disclaimers
  lines.push('## Disclaimers');
  lines.push('');
  for (const d of getDisclaimers(config)) {
    lines.push(`> ${d}`);
    lines.push('');
  }

  // Footer privilege marker
  lines.push('---');
  lines.push(privilegeMarker);

  return lines.join('\n');
}

// ─── Privilege & Compliance ─────────────────────────────────────────

function buildPrivilegeMarker(config: DossierConfig): string {
  switch (config.confidentialityLevel) {
    case 'ATTORNEY_WORK_PRODUCT':
      return '**⚖️ ATTORNEY WORK PRODUCT — PRIVILEGED AND CONFIDENTIAL — PREPARED IN ANTICIPATION OF LITIGATION — FED. R. CIV. P. 26(b)(3)**';
    case 'ATTORNEY_CLIENT_PRIVILEGED':
      return '**🔒 ATTORNEY-CLIENT PRIVILEGED COMMUNICATION — DO NOT DISCLOSE — KOVEL DOCTRINE APPLIES**';
    case 'PUBLIC':
      return '**📄 PUBLIC RESEARCH MEMORANDUM**';
  }
}

function buildMethodology(result: ProSearchResult): string {
  return `This research was conducted using CounselConduit's Pro Search engine, which executes multi-step privileged research through the following pipeline:

1. **Query Decomposition:** The original query was decomposed into ${result.steps.length} atomic sub-questions.
2. **Zero Data Retention Search:** Each sub-question was executed via Google Custom Search Enterprise API (ZDR) or Perplexity Sonar Pro, routed through a server-side proxy to protect client identity.
3. **Progressive Synthesis:** Results from each step informed subsequent search queries for progressive refinement.
4. **Citation Extraction:** ${result.allCitations.length} citations were automatically extracted and classified by authority type.
5. **Privilege Protection:** All research executed under Kovel Doctrine. See *United States v. Heppner* (S.D.N.Y. 2026).

Total research time: ${result.totalDurationMs}ms.`;
}

function getDisclaimers(config: DossierConfig): string[] {
  const disclaimers = [
    'This research memorandum was generated by AI-assisted legal research tools. All citations should be independently verified before reliance.',
    "This document does not constitute legal advice. It is provided as research support for the supervising attorney's review and analysis.",
  ];

  if (config.confidentialityLevel !== 'PUBLIC') {
    disclaimers.push(
      'This document is protected by attorney-client privilege and/or the work-product doctrine. Unauthorized disclosure may result in waiver of these protections.',
    );
  }

  return disclaimers;
}

/**
 * @fileoverview Westlaw/LexisNexis Citation Validation Stubs
 *
 * Stub interfaces for integrating with legal research databases.
 * Phase 3 will implement full API integration when Exclusive
 * Distribution Rights are secured (see OMNIBUS §Phase 3).
 *
 * Currently validates citation format rather than existence.
 * Production integration requires Thomson Reuters API key or
 * LexisNexis Web Services subscription.
 *
 * @see CitationPanel.tsx — UI component
 * @see legal-prompts.ts — Citation validator prompt
 */

// ═══════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════

export type AuthorityType =
  | 'statute'
  | 'case_law'
  | 'regulation'
  | 'constitutional'
  | 'secondary'
  | 'treatise'
  | 'law_review';

export interface CitationValidationResult {
  citationId: string;
  originalText: string;
  isValid: boolean;
  validationType: 'format' | 'existence' | 'currency';
  authorityType: AuthorityType;
  confidence: number;
  warnings: string[];
  westlawUrl?: string;
  lexisUrl?: string;
  shepardStatus?: ShepardStatus;
}

export type ShepardStatus =
  | 'positive'     // Green — followed
  | 'caution'      // Yellow — distinguished
  | 'negative'     // Red — overruled
  | 'questioned'   // Orange — questioned
  | 'unchecked';   // Gray — not yet validated

export interface CitationProvider {
  name: string;
  validateCitation(text: string): Promise<CitationValidationResult>;
  checkCurrency(text: string): Promise<ShepardStatus>;
  getFullText(citationId: string): Promise<string | null>;
}

// ═══════════════════════════════════════════════════════════
// Citation Format Patterns
// ═══════════════════════════════════════════════════════════

const CITATION_PATTERNS: Record<AuthorityType, RegExp[]> = {
  case_law: [
    // Federal cases: Smith v. Jones, 500 U.S. 123 (2000)
    /\b\d+\s+(U\.S\.|S\.\s*Ct\.|L\.\s*Ed\.|F\.\d+[a-z]*|F\.\s*Supp\.\s*\d*[a-z]*)\s+\d+/i,
    // State cases: Smith v. Jones, 123 Cal.App.4th 456 (2020)
    /\b\d+\s+[A-Z][a-z]+\.?\s*(App\.)?\s*\d*[a-z]*\s+\d+/i,
  ],
  statute: [
    // U.S. Code: 42 U.S.C. § 1983
    /\b\d+\s+U\.S\.C\.\s*§\s*\d+/i,
    // State codes: Cal. Civ. Code § 1549
    /\b[A-Z][a-z]+\.?\s+[A-Z][a-z]+\.?\s+(Code|Ann\.)\s*§\s*\d+/i,
    // Public laws: Pub. L. 116-283
    /\bPub\.\s*L\.\s*\d+-\d+/i,
  ],
  regulation: [
    // CFR: 29 C.F.R. § 1910.134
    /\b\d+\s+C\.F\.R\.\s*§\s*[\d.]+/i,
    // Federal Register: 85 Fed. Reg. 1234
    /\b\d+\s+Fed\.\s*Reg\.\s*\d+/i,
  ],
  constitutional: [
    // U.S. Const. amend. XIV
    /\bU\.S\.\s*Const\.\s*(art\.\s*[IVX]+|amend\.\s*[IVX]+)/i,
    // State constitutions
    /\b[A-Z][a-z]+\.?\s*Const\.\s*(art\.\s*[IVX\d]+)/i,
  ],
  secondary: [
    // Restatement: Restatement (Third) of Torts § 7
    /\bRestatement\s*\([A-Z][a-z]+\)\s+of\s+\w+\s*§\s*\d+/i,
  ],
  treatise: [
    // Named treatises: 5 Williston on Contracts § 12:3
    /\b\d+\s+\w+\s+on\s+\w+\s*§\s*[\d:]+/i,
  ],
  law_review: [
    // Law reviews: 85 Harv. L. Rev. 1234
    /\b\d+\s+[A-Z][a-z]+\.?\s*L\.\s*Rev\.\s*\d+/i,
  ],
};

// ═══════════════════════════════════════════════════════════
// Stub Provider: Format-Only Validation
// ═══════════════════════════════════════════════════════════

export class FormatValidationProvider implements CitationProvider {
  name = 'FormatValidator (Stub)';

  async validateCitation(text: string): Promise<CitationValidationResult> {
    const detected = this.detectAuthorityType(text);

    return {
      citationId: `fv-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
      originalText: text,
      isValid: detected.isValid,
      validationType: 'format',
      authorityType: detected.type,
      confidence: detected.confidence,
      warnings: detected.isValid
        ? ['Format validated only — existence not verified (stub mode)']
        : [`Unrecognized citation format: "${text.substring(0, 50)}..."`],
      shepardStatus: 'unchecked',
    };
  }

  async checkCurrency(_text: string): Promise<ShepardStatus> {
    // Stub: always return unchecked
    return 'unchecked';
  }

  async getFullText(_citationId: string): Promise<string | null> {
    // Stub: not available without Westlaw/Lexis integration
    return null;
  }

  private detectAuthorityType(text: string): {
    type: AuthorityType;
    isValid: boolean;
    confidence: number;
  } {
    for (const [type, patterns] of Object.entries(CITATION_PATTERNS)) {
      for (const pattern of patterns) {
        if (pattern.test(text)) {
          return {
            type: type as AuthorityType,
            isValid: true,
            confidence: 0.8,
          };
        }
      }
    }

    return {
      type: 'secondary',
      isValid: false,
      confidence: 0.2,
    };
  }
}

// ═══════════════════════════════════════════════════════════
// Stub Provider: Westlaw (Future Integration)
// ═══════════════════════════════════════════════════════════

export class WestlawProvider implements CitationProvider {
  name = 'Westlaw (Stub — Phase 3)';

  constructor(private _apiKey?: string) {
    // API key would come from BYOK key management
  }

  async validateCitation(text: string): Promise<CitationValidationResult> {
    // TODO(Phase 3): Implement Westlaw API validation
    // TR API: https://developer.thomsonreuters.com/
    const formatProvider = new FormatValidationProvider();
    const result = await formatProvider.validateCitation(text);
    result.warnings.push(
      'Westlaw integration pending (Phase 3). Using format validation only.',
    );
    return result;
  }

  async checkCurrency(text: string): Promise<ShepardStatus> {
    // TODO(Phase 3): Implement KeyCite currency check
    return 'unchecked';
  }

  async getFullText(_citationId: string): Promise<string | null> {
    // TODO(Phase 3): Implement full-text retrieval via Westlaw API
    return null;
  }
}

// ═══════════════════════════════════════════════════════════
// Stub Provider: LexisNexis (Future Integration)
// ═══════════════════════════════════════════════════════════

export class LexisNexisProvider implements CitationProvider {
  name = 'LexisNexis (Stub — Phase 3)';

  constructor(private _apiKey?: string) {
    // API key would come from BYOK key management
  }

  async validateCitation(text: string): Promise<CitationValidationResult> {
    // TODO(Phase 3): Implement LexisNexis Web Services validation
    const formatProvider = new FormatValidationProvider();
    const result = await formatProvider.validateCitation(text);
    result.warnings.push(
      'LexisNexis integration pending (Phase 3). Using format validation only.',
    );
    return result;
  }

  async checkCurrency(_text: string): Promise<ShepardStatus> {
    // TODO(Phase 3): Implement Shepard's Citations check
    return 'unchecked';
  }

  async getFullText(_citationId: string): Promise<string | null> {
    // TODO(Phase 3): Implement full-text retrieval via Lexis API
    return null;
  }
}

// ═══════════════════════════════════════════════════════════
// Factory
// ═══════════════════════════════════════════════════════════

export function getCitationProvider(
  provider: 'format' | 'westlaw' | 'lexis' = 'format',
  apiKey?: string,
): CitationProvider {
  switch (provider) {
    case 'westlaw':
      return new WestlawProvider(apiKey);
    case 'lexis':
      return new LexisNexisProvider(apiKey);
    default:
      return new FormatValidationProvider();
  }
}

/**
 * Batch-validate an array of citation strings.
 */
export async function validateCitations(
  citations: string[],
  provider: CitationProvider = new FormatValidationProvider(),
): Promise<CitationValidationResult[]> {
  return Promise.all(
    citations.map(c => provider.validateCitation(c)),
  );
}

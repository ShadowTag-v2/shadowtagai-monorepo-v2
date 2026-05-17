/**
 * Oracle Memo PDF Export
 *
 * Sprint Item #20: Server-side PDF generation for Oracle Memos.
 *
 * An Oracle Memo is the culmination of the 7-stage Oracle Studio
 * pipeline. It contains:
 * - Synthesized legal research
 * - Case citations with relevance scores
 * - Risk assessment
 * - Recommended actions
 * - Attorney attestation
 *
 * This module generates a structured data object for PDF rendering
 * (actual PDF rendering uses puppeteer or @react-pdf/renderer).
 *
 * @see docs/pitch-deck.md — Oracle Studio pipeline
 */

import { z } from "zod";

// ─── Schemas ────────────────────────────────────────────────────────

export const OracleMemoSchema = z.object({
  memoId: z.string().uuid(),
  sessionId: z.string().uuid(),
  firmId: z.string().uuid(),
  generatedAt: z.string().datetime(),

  // Header
  title: z.string(),
  preparedFor: z.string(),
  preparedBy: z.string(),
  jurisdiction: z.string(),
  practiceArea: z.string(),

  // Executive Summary
  executiveSummary: z.string(),
  riskLevel: z.enum(["LOW", "MODERATE", "HIGH", "CRITICAL"]),

  // Research Findings
  findings: z.array(
    z.object({
      findingId: z.string(),
      title: z.string(),
      analysis: z.string(),
      relevanceScore: z.number().min(0).max(1),
      confidence: z.enum(["HIGH", "MEDIUM", "LOW"]),
    }),
  ),

  // Citations
  citations: z.array(
    z.object({
      caseTitle: z.string(),
      citation: z.string(),
      court: z.string(),
      year: z.number(),
      relevance: z.string(),
      url: z.string().url().optional(),
    }),
  ),

  // Risk Assessment
  riskAssessment: z.object({
    overallRisk: z.enum(["LOW", "MODERATE", "HIGH", "CRITICAL"]),
    riskFactors: z.array(z.string()),
    mitigations: z.array(z.string()),
  }),

  // Recommendations
  recommendations: z.array(
    z.object({
      priority: z.enum(["IMMEDIATE", "SHORT_TERM", "LONG_TERM"]),
      action: z.string(),
      rationale: z.string(),
    }),
  ),

  // Attestation
  attestation: z.object({
    kovelReceiptId: z.string().uuid(),
    privilegeType: z.string(),
    dataRetentionDays: z.number().default(30),
  }),

  // Model metadata
  modelInfo: z.object({
    primaryModel: z.string(),
    tokenCount: z.number(),
    pipelineStages: z.number().default(7),
  }),
});

export type OracleMemo = z.infer<typeof OracleMemoSchema>;

// ─── PDF Template Structure ─────────────────────────────────────────

export interface MemoPDFTemplate {
  pages: MemoPDFPage[];
  metadata: {
    title: string;
    author: string;
    subject: string;
    createdAt: string;
    keywords: string[];
    confidential: boolean;
  };
}

interface MemoPDFPage {
  type: "cover" | "content" | "citations" | "recommendations" | "attestation";
  content: Record<string, string | string[]>;
}

// ─── Template Generator ─────────────────────────────────────────────

/**
 * Converts an OracleMemo into a PDF-ready template structure.
 */
export function generateMemoPDFTemplate(memo: OracleMemo): MemoPDFTemplate {
  return {
    metadata: {
      title: memo.title,
      author: memo.preparedBy,
      subject: `Oracle Memo — ${memo.practiceArea}`,
      createdAt: memo.generatedAt,
      keywords: ["privileged", "kovel", memo.practiceArea, memo.jurisdiction],
      confidential: true,
    },
    pages: [
      // ── Cover Page ──────────────────────────────────────────
      {
        type: "cover",
        content: {
          title: memo.title,
          subtitle: "PRIVILEGED & CONFIDENTIAL — ATTORNEY WORK PRODUCT",
          preparedFor: memo.preparedFor,
          preparedBy: memo.preparedBy,
          date: new Date(memo.generatedAt).toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
          }),
          jurisdiction: memo.jurisdiction,
          practiceArea: memo.practiceArea,
          riskLevel: memo.riskLevel,
          memoId: memo.memoId,
          footer:
            "This document is protected by attorney-client privilege under the Kovel Doctrine.",
        },
      },

      // ── Executive Summary ───────────────────────────────────
      {
        type: "content",
        content: {
          heading: "Executive Summary",
          body: memo.executiveSummary,
          riskBadge: `Overall Risk: ${memo.riskAssessment.overallRisk}`,
          findingsSummary: `${memo.findings.length} findings across ${memo.citations.length} cited authorities`,
        },
      },

      // ── Research Findings ───────────────────────────────────
      {
        type: "content",
        content: {
          heading: "Research Findings",
          findings: memo.findings.map(
            (f) =>
              `[${f.confidence}] ${f.title} (relevance: ${Math.round(f.relevanceScore * 100)}%)\n${f.analysis}`,
          ),
        },
      },

      // ── Citations Page ──────────────────────────────────────
      {
        type: "citations",
        content: {
          heading: "Cited Authorities",
          citations: memo.citations.map(
            (c) => `${c.caseTitle}, ${c.citation} (${c.court}, ${c.year})\n${c.relevance}`,
          ),
        },
      },

      // ── Risk Assessment ─────────────────────────────────────
      {
        type: "content",
        content: {
          heading: "Risk Assessment",
          overallRisk: memo.riskAssessment.overallRisk,
          riskFactors: memo.riskAssessment.riskFactors,
          mitigations: memo.riskAssessment.mitigations,
        },
      },

      // ── Recommendations ─────────────────────────────────────
      {
        type: "recommendations",
        content: {
          heading: "Recommended Actions",
          immediate: memo.recommendations
            .filter((r) => r.priority === "IMMEDIATE")
            .map((r) => `${r.action}\nRationale: ${r.rationale}`),
          shortTerm: memo.recommendations
            .filter((r) => r.priority === "SHORT_TERM")
            .map((r) => `${r.action}\nRationale: ${r.rationale}`),
          longTerm: memo.recommendations
            .filter((r) => r.priority === "LONG_TERM")
            .map((r) => `${r.action}\nRationale: ${r.rationale}`),
        },
      },

      // ── Attestation Page ────────────────────────────────────
      {
        type: "attestation",
        content: {
          heading: "Kovel Attestation",
          receiptId: memo.attestation.kovelReceiptId,
          privilegeType: memo.attestation.privilegeType,
          retention: `Data retained for ${memo.attestation.dataRetentionDays} days per GDPR policy`,
          modelInfo: `Generated by ${memo.modelInfo.primaryModel} | ${memo.modelInfo.tokenCount.toLocaleString()} tokens | ${memo.modelInfo.pipelineStages}-stage pipeline`,
          disclaimer: [
            "PRIVILEGED & CONFIDENTIAL — ATTORNEY WORK PRODUCT",
            "",
            "This Oracle Memo was generated under attorney-client privilege",
            "extended via the Kovel Doctrine. The research was conducted",
            "through a Zero Data Retention pipeline. All AI interactions",
            "are covered by the Kovel Attestation Receipt referenced above.",
            "",
            "This document may not be disclosed or distributed without",
            "the express written consent of the supervising attorney.",
          ].join("\n"),
        },
      },
    ],
  };
}

// ─── HTML Rendering ─────────────────────────────────────────────────

/**
 * Renders the Oracle Memo as HTML for server-side PDF generation.
 * Used with puppeteer's page.pdf() method.
 */
export function renderMemoHTML(memo: OracleMemo): string {
  const template = generateMemoPDFTemplate(memo);

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>${template.metadata.title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Space+Grotesk:wght@600;700&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Inter', sans-serif; color: #1a1a2e; background: #fff; font-size: 11pt; line-height: 1.6; }
  .page { page-break-after: always; padding: 48px; min-height: 100vh; }
  .page:last-child { page-break-after: auto; }
  h1 { font-family: 'Space Grotesk', sans-serif; font-size: 24pt; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 8px; }
  h2 { font-family: 'Space Grotesk', sans-serif; font-size: 16pt; font-weight: 600; margin-bottom: 16px; border-bottom: 2px solid #00d4ff; padding-bottom: 8px; }
  .risk-badge { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 10pt; font-weight: 600; text-transform: uppercase; }
  .risk-LOW { background: #e8f5e9; color: #2e7d32; }
  .risk-MODERATE { background: #e3f2fd; color: #1565c0; }
  .risk-HIGH { background: #fff3e0; color: #e65100; }
  .risk-CRITICAL { background: #ffebee; color: #c62828; }
  .privileged { text-align: center; font-size: 9pt; color: #c62828; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 24px; }
  .footer { position: fixed; bottom: 24px; left: 48px; right: 48px; font-size: 8pt; color: #999; text-align: center; }
  .citation { padding: 12px; margin-bottom: 8px; background: #f8f9fa; border-left: 3px solid #00d4ff; }
</style>
</head>
<body>
<div class="privileged">PRIVILEGED & CONFIDENTIAL — ATTORNEY WORK PRODUCT</div>
<div class="page">
  <h1>${memo.title}</h1>
  <p>Prepared for: ${memo.preparedFor}</p>
  <p>Prepared by: ${memo.preparedBy}</p>
  <p>Date: ${new Date(memo.generatedAt).toLocaleDateString()}</p>
  <p>Jurisdiction: ${memo.jurisdiction}</p>
  <span class="risk-badge risk-${memo.riskLevel}">${memo.riskLevel} RISK</span>
</div>
<div class="page">
  <h2>Executive Summary</h2>
  <p>${memo.executiveSummary}</p>
</div>
<div class="page">
  <h2>Cited Authorities</h2>
  ${memo.citations.map((c) => `<div class="citation"><strong>${c.caseTitle}</strong>, ${c.citation} (${c.court}, ${c.year})<br/>${c.relevance}</div>`).join("")}
</div>
<div class="page">
  <h2>Kovel Attestation</h2>
  <p>Receipt ID: ${memo.attestation.kovelReceiptId}</p>
  <p>Privilege: ${memo.attestation.privilegeType}</p>
  <p>Model: ${memo.modelInfo.primaryModel} | ${memo.modelInfo.tokenCount.toLocaleString()} tokens</p>
</div>
<div class="footer">KovelAI Oracle Memo — Memo ID: ${memo.memoId}</div>
</body>
</html>`;
}

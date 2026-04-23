/**
 * Insurance Compliance Verification API
 *
 * Verifies that a law firm's malpractice insurance meets the
 * minimum requirements for KovelAI platform participation.
 *
 * Nag Protocol #14: Insurance compliance verification API
 */
import { type NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const InsuranceVerifySchema = z.object({
  firmId: z.string().uuid(),
  policyNumber: z.string().min(1).max(100),
  carrierName: z.string().min(1).max(200),
  coverageAmount: z.number().min(100_000),
  deductible: z.number().min(0),
  expiryDate: z.string().datetime(),
  coverageType: z.enum([
    'PROFESSIONAL_LIABILITY',
    'ERRORS_OMISSIONS',
    'CYBER_LIABILITY',
    'GENERAL_LIABILITY',
  ]),
  stateBarNumber: z.string().min(1),
  jurisdiction: z.string().min(2).max(10),
});

// Minimum coverage requirements by tier
const TIER_REQUIREMENTS = {
  solo: { minCoverage: 250_000, maxDeductible: 25_000 },
  practice: { minCoverage: 500_000, maxDeductible: 50_000 },
  enterprise: { minCoverage: 2_000_000, maxDeductible: 100_000 },
} as const;

// Approved carriers (subset — full list from insurance alliance)
const APPROVED_CARRIERS = new Set([
  'CNA',
  'Travelers',
  'AIG',
  'Swiss Re',
  'Hartford',
  'Zurich',
  'Chubb',
  'Berkshire Hathaway',
  "Lloyd's",
  'Hiscox',
  'ALPS',
  'Lawyers Mutual',
  'Minnesota Lawyers Mutual',
]);

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const body = await req.json();
    const parsed = InsuranceVerifySchema.parse(body);

    const issues: string[] = [];
    const warnings: string[] = [];

    // Check expiry
    const expiryDate = new Date(parsed.expiryDate);
    const now = new Date();
    const daysUntilExpiry = Math.floor(
      (expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24),
    );

    if (daysUntilExpiry < 0) {
      issues.push(`Policy expired ${Math.abs(daysUntilExpiry)} days ago`);
    } else if (daysUntilExpiry < 30) {
      warnings.push(`Policy expires in ${daysUntilExpiry} days — renewal required`);
    }

    // Check minimum coverage (default to solo tier)
    const tier = 'solo'; // Could be resolved from firm profile
    const requirements = TIER_REQUIREMENTS[tier];

    if (parsed.coverageAmount < requirements.minCoverage) {
      issues.push(
        `Coverage $${parsed.coverageAmount.toLocaleString()} below minimum $${requirements.minCoverage.toLocaleString()} for ${tier} tier`,
      );
    }

    if (parsed.deductible > requirements.maxDeductible) {
      warnings.push(
        `Deductible $${parsed.deductible.toLocaleString()} exceeds recommended maximum $${requirements.maxDeductible.toLocaleString()}`,
      );
    }

    // Check carrier approval
    const isApprovedCarrier = APPROVED_CARRIERS.has(parsed.carrierName);
    if (!isApprovedCarrier) {
      warnings.push(
        `Carrier "${parsed.carrierName}" not in approved list — manual review required`,
      );
    }

    // Check coverage type
    if (
      parsed.coverageType !== 'PROFESSIONAL_LIABILITY' &&
      parsed.coverageType !== 'ERRORS_OMISSIONS'
    ) {
      warnings.push(
        `Coverage type "${parsed.coverageType}" may not satisfy malpractice requirements — verify with bar`,
      );
    }

    const status = issues.length > 0 ? 'FAILED' : warnings.length > 0 ? 'CONDITIONAL' : 'VERIFIED';

    return NextResponse.json({
      status,
      firmId: parsed.firmId,
      policyNumber: parsed.policyNumber,
      carrierName: parsed.carrierName,
      coverageAmount: parsed.coverageAmount,
      daysUntilExpiry,
      isApprovedCarrier,
      issues,
      warnings,
      verifiedAt: new Date().toISOString(),
      nextReviewDate:
        status === 'VERIFIED'
          ? new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString()
          : new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json({ error: 'Insurance verification failed' }, { status: 500 });
  }
}

/**
 * CLE Certificate Generation Endpoint
 *
 * Item #9: POST /api/cle/generate
 *
 * Generates a CLE certificate after verifying:
 * - Attorney bar number
 * - Course completion (90%+ attendance)
 * - Heartbeat integrity
 * - Firm subscription tier allows CLE
 *
 * @see lib/compliance/cle-certificate.ts
 */

import { type NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import {
  CLE_COURSES,
  generateCLECertificate,
  getCertificatePDFData,
} from '@/lib/compliance/cle-certificate';

// ─── Request Schema ─────────────────────────────────────────────────

const GenerateCLERequestSchema = z.object({
  attorneyName: z.string().min(1).max(200),
  barNumber: z.string().min(1).max(50),
  jurisdiction: z.string().min(1).max(100),
  firmName: z.string().min(1).max(200),
  courseId: z.string().min(1),
  courseDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  attendanceMinutes: z.number().int().min(1),
  heartbeatCount: z.number().int().min(1),
});

// ─── Handler ────────────────────────────────────────────────────────

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const body = await req.json();
    const parsed = GenerateCLERequestSchema.parse(body);

    const result = generateCLECertificate(parsed);

    if ('error' in result) {
      return NextResponse.json({ error: result.error }, { status: 422 });
    }

    const pdfData = getCertificatePDFData(result);

    return NextResponse.json({
      certificate: result,
      pdfData,
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json({ error: 'Certificate generation failed' }, { status: 500 });
  }
}

// ─── GET: List Available Courses ────────────────────────────────────

export async function GET(): Promise<NextResponse> {
  return NextResponse.json({
    courses: CLE_COURSES.map((c) => ({
      id: c.id,
      title: c.title,
      description: c.description,
      creditHours: c.creditHours,
      creditType: c.creditType,
      accreditedStates: c.accreditedStates,
    })),
  });
}

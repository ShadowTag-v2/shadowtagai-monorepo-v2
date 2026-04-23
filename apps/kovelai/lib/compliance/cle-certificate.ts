/**
 * CLE Certificate Generator
 *
 * Sprint Item #17: Automated Continuing Legal Education certificates.
 *
 * Generates PDF-ready CLE certificate data for attorneys who
 * complete CLE sessions conducted through the KovelAI platform.
 *
 * Flow:
 * 1. Attorney watches CLE content via platform
 * 2. System tracks attendance via session heartbeat
 * 3. On completion, this module generates certificate data
 * 4. Certificate rendered as PDF (server-side)
 *
 * @see docs/cle-seminar-deck.md — CLE content reference
 */

import { z } from 'zod';

// ─── Schemas ────────────────────────────────────────────────────────

export const CLECertificateSchema = z.object({
  certificateId: z.string().uuid(),
  attorneyName: z.string(),
  barNumber: z.string(),
  jurisdiction: z.string(),
  firmName: z.string(),

  // Course details
  courseTitle: z.string(),
  courseDescription: z.string(),
  courseDate: z.string(), // YYYY-MM-DD
  creditHours: z.number().min(0.5).max(8),
  creditType: z.enum(['GENERAL', 'ETHICS', 'PROFESSIONAL_RESPONSIBILITY', 'TECHNOLOGY']),
  deliveryMethod: z.enum(['LIVE_WEBINAR', 'ON_DEMAND', 'IN_PERSON']),

  // Attendance verification
  attendanceMinutes: z.number().int(),
  heartbeatCount: z.number().int(), // How many heartbeats recorded
  completionPercentage: z.number().min(0).max(100),

  // Verification
  verificationCode: z.string(), // 8-char alphanumeric
  issuedAt: z.string().datetime(),
  validUntil: z.string().datetime(), // Typically 1 year for reporting

  // Accreditation
  providerName: z.string().default('KovelAI Legal Technology'),
  providerNumber: z.string().optional(), // State bar provider number
  accreditedStates: z.array(z.string()),
});

export type CLECertificate = z.infer<typeof CLECertificateSchema>;

// ─── Available Courses ──────────────────────────────────────────────

export const CLE_COURSES = [
  {
    id: 'CLE-001',
    title: 'AI-Privileged Legal Research: The Kovel Doctrine in the Digital Age',
    description:
      'Understanding how attorney-client privilege extends to AI-assisted research under United States v. Heppner (S.D.N.Y. 2026).',
    creditHours: 1.5,
    creditType: 'TECHNOLOGY' as const,
    accreditedStates: ['NY', 'CA', 'IL', 'TX', 'FL', 'PA', 'NJ'],
  },
  {
    id: 'CLE-002',
    title: 'Ethics of AI in Legal Practice: Competence and Confidentiality',
    description:
      'Model Rule 1.1 competence requirements for attorneys using AI tools, and Model Rule 1.6 confidentiality obligations.',
    creditHours: 2.0,
    creditType: 'ETHICS' as const,
    accreditedStates: ['NY', 'CA', 'IL', 'TX', 'FL', 'PA', 'NJ', 'MA', 'DC'],
  },
  {
    id: 'CLE-003',
    title: 'Privilege Waiver in the Age of Public AI',
    description:
      'How using ChatGPT, Claude, and Gemini on consumer platforms can waive attorney-client privilege, and how to prevent it.',
    creditHours: 1.0,
    creditType: 'PROFESSIONAL_RESPONSIBILITY' as const,
    accreditedStates: ['NY', 'CA', 'IL', 'TX', 'FL'],
  },
];

// ─── Certificate Generation ─────────────────────────────────────────

interface GenerateCertificateRequest {
  attorneyName: string;
  barNumber: string;
  jurisdiction: string;
  firmName: string;
  courseId: string;
  courseDate: string;
  attendanceMinutes: number;
  heartbeatCount: number;
}

/**
 * Generates a CLE certificate after verifying completion requirements.
 */
export function generateCLECertificate(
  request: GenerateCertificateRequest,
): CLECertificate | { error: string } {
  const course = CLE_COURSES.find((c) => c.id === request.courseId);
  if (!course) {
    return { error: `Course ${request.courseId} not found` };
  }

  // Verify minimum attendance (must complete at least 90% of course)
  const requiredMinutes = course.creditHours * 60;
  const completionPercentage = Math.round((request.attendanceMinutes / requiredMinutes) * 100);

  if (completionPercentage < 90) {
    return {
      error: `Insufficient attendance: ${completionPercentage}% (minimum 90% required)`,
    };
  }

  // Verify heartbeat integrity (minimum 1 heartbeat per 5 minutes)
  const expectedHeartbeats = Math.floor(request.attendanceMinutes / 5);
  if (request.heartbeatCount < expectedHeartbeats * 0.8) {
    return {
      error: `Heartbeat verification failed: ${request.heartbeatCount}/${expectedHeartbeats} expected`,
    };
  }

  const verificationCode = generateVerificationCode();
  const now = new Date();
  const validUntil = new Date(now);
  validUntil.setFullYear(validUntil.getFullYear() + 1);

  return {
    certificateId: crypto.randomUUID(),
    attorneyName: request.attorneyName,
    barNumber: request.barNumber,
    jurisdiction: request.jurisdiction,
    firmName: request.firmName,
    courseTitle: course.title,
    courseDescription: course.description,
    courseDate: request.courseDate,
    creditHours: course.creditHours,
    creditType: course.creditType,
    deliveryMethod: 'LIVE_WEBINAR',
    attendanceMinutes: request.attendanceMinutes,
    heartbeatCount: request.heartbeatCount,
    completionPercentage,
    verificationCode,
    issuedAt: now.toISOString(),
    validUntil: validUntil.toISOString(),
    providerName: 'KovelAI Legal Technology',
    accreditedStates: course.accreditedStates,
  };
}

// ─── Verification ───────────────────────────────────────────────────

/**
 * Verifies a CLE certificate by its verification code.
 */
export function verifyCertificate(certificate: CLECertificate, verificationCode: string): boolean {
  return (
    certificate.verificationCode === verificationCode &&
    new Date(certificate.validUntil) > new Date()
  );
}

// ─── PDF Template Data ──────────────────────────────────────────────

/**
 * Generates the data structure needed for PDF rendering.
 */
export function getCertificatePDFData(cert: CLECertificate): Record<string, string> {
  return {
    title: 'CERTIFICATE OF CONTINUING LEGAL EDUCATION',
    subtitle: 'This certifies that',
    name: cert.attorneyName,
    barInfo: `Bar Number: ${cert.barNumber} | Jurisdiction: ${cert.jurisdiction}`,
    courseInfo: `has successfully completed ${cert.creditHours} hours of ${cert.creditType} credit`,
    courseTitle: cert.courseTitle,
    date: `Date: ${cert.courseDate}`,
    provider: cert.providerName,
    verification: `Verification Code: ${cert.verificationCode}`,
    issued: `Issued: ${new Date(cert.issuedAt).toLocaleDateString()}`,
    valid: `Valid Until: ${new Date(cert.validUntil).toLocaleDateString()}`,
    states: `Accredited in: ${cert.accreditedStates.join(', ')}`,
  };
}

// ─── Helpers ────────────────────────────────────────────────────────

function generateVerificationCode(): string {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // No I, O, 0, 1 for readability
  let code = '';
  for (let i = 0; i < 8; i++) {
    code += chars[Math.floor(Math.random() * chars.length)];
  }
  return code;
}

/**
 * Client Intake Magic Link Generator
 *
 * Generates a secure, time-limited magic link for new client intake.
 * When a prospective client receives this link, they enter a
 * Kovel-protected session that:
 * 1. Creates a 24-hour bounded sandbox
 * 2. Mints an S.E.U. proxy token
 * 3. Enables privileged search
 * 4. Auto-evaporates after expiry (Heppner doctrine)
 *
 * Nag Protocol #15: Build client intake Magic Link generator
 */

import { randomUUID } from 'node:crypto';
import jwt from 'jsonwebtoken';
import { type NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const MagicLinkSchema = z.object({
  firmId: z.string().uuid(),
  lawyerId: z.string().uuid(),
  clientEmail: z.string().email(),
  clientName: z.string().min(1).max(200),
  practiceArea: z.string().min(1).max(100),
  jurisdiction: z.string().min(2).max(50),
  expiryHours: z.number().min(1).max(72).default(24),
  notes: z.string().max(2000).optional(),
});

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const body = await req.json();
    const parsed = MagicLinkSchema.parse(body);

    const linkId = randomUUID();
    const expiresAt = new Date(Date.now() + parsed.expiryHours * 60 * 60 * 1000);

    // Create a signed intake token
    const token = jwt.sign(
      {
        jti: linkId,
        type: 'client_intake',
        firmId: parsed.firmId,
        lawyerId: parsed.lawyerId,
        clientEmail: parsed.clientEmail,
        clientName: parsed.clientName,
        practiceArea: parsed.practiceArea,
        jurisdiction: parsed.jurisdiction,
        iss: 'kovelai-intake',
      },
      getIntakeSecret(),
      {
        expiresIn: `${parsed.expiryHours}h`,
        algorithm: 'HS512',
      },
    );

    // Base URL for the intake portal
    const baseUrl = process.env.KOVELAI_BASE_URL ?? 'https://kovelai.web.app';
    const magicLink = `${baseUrl}/intake?token=${token}`;

    // Queue welcome email via Cloud Tasks
    const cloudTasksUrl = process.env.CLOUD_TASKS_QUEUE_URL;
    if (cloudTasksUrl) {
      fetch(cloudTasksUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task: 'send_intake_magic_link',
          payload: {
            recipientEmail: parsed.clientEmail,
            recipientName: parsed.clientName,
            magicLink,
            firmId: parsed.firmId,
            expiresAt: expiresAt.toISOString(),
            lawyerNotes: parsed.notes,
          },
        }),
      }).catch(() => {
        /* Cloud Tasks queue is fire-and-forget */
      });
    }

    return NextResponse.json({
      linkId,
      magicLink,
      expiresAt: expiresAt.toISOString(),
      clientEmail: parsed.clientEmail,
      status: 'GENERATED',
      deliveryStatus: cloudTasksUrl ? 'EMAIL_QUEUED' : 'EMAIL_NOT_CONFIGURED',
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json({ error: 'Magic link generation failed' }, { status: 500 });
  }
}

function getIntakeSecret(): string {
  const secret = process.env.KOVELAI_INTAKE_SECRET;
  if (!secret || secret.length < 32) {
    throw new Error('[INTAKE] KOVELAI_INTAKE_SECRET must be set and at least 32 characters');
  }
  return secret;
}

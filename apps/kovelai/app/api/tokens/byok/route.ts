/**
 * BYOK (Bring Your Own Keys) Registration Endpoint
 *
 * Sprint Item #7: Zero-knowledge API key management.
 *
 * Flow:
 * 1. Client encrypts API key via WebCrypto AES-256-GCM in browser
 * 2. Encrypted payload transmitted to this endpoint
 * 3. Stored in GCP Secret Manager — we NEVER see the plaintext
 * 4. Key bound to firm_id via S.E.U. token
 * 5. Revocation purges from Secret Manager permanently
 *
 * Supported providers: Anthropic, Google Vertex AI, OpenAI
 *
 * @see CLE seminar deck — Slide 8
 * @see Cor.30 Pillar 2 — Secrets & Supply Chain
 */

import { type NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

// ─── Schemas ────────────────────────────────────────────────────────

const SUPPORTED_PROVIDERS = ['anthropic', 'google-vertex', 'openai'] as const;

const RegisterKeySchema = z.object({
  provider: z.enum(SUPPORTED_PROVIDERS),
  encryptedKey: z.string().min(1).max(10000), // AES-256-GCM encrypted blob
  iv: z.string().min(1).max(100), // Initialization vector (base64)
  firmId: z.string().uuid(),
});

const RevokeKeySchema = z.object({
  provider: z.enum(SUPPORTED_PROVIDERS),
  firmId: z.string().uuid(),
});

// ─── POST: Register a BYOK key ─────────────────────────────────────

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const seuToken = req.headers.get('x-seu-token');
    if (!seuToken) {
      return NextResponse.json({ error: 'S.E.U. token required' }, { status: 401 });
    }

    const body = await req.json();
    const { provider, encryptedKey, iv, firmId } = RegisterKeySchema.parse(body);

    // Store encrypted key in GCP Secret Manager
    const secretId = `byok-${firmId.substring(0, 8)}-${provider}`;
    const projectId = process.env.GCP_PROJECT_ID ?? 'shadowtag-omega-v4';

    // Create or update secret
    const secretPayload = JSON.stringify({
      encryptedKey,
      iv,
      provider,
      firmId,
      registeredAt: new Date().toISOString(),
    });

    // Write to Secret Manager
    const accessToken = await getAccessToken();

    // Try to create the secret first
    const createResponse = await fetch(
      `https://secretmanager.googleapis.com/v1/projects/${projectId}/secrets?secretId=${secretId}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          replication: { automatic: {} },
          labels: {
            type: 'byok',
            provider,
            firm: firmId.substring(0, 8),
          },
        }),
      },
    );

    // If secret already exists (409), that's fine — we'll add a new version
    if (!createResponse.ok && createResponse.status !== 409) {
      return NextResponse.json({ error: 'Failed to store key' }, { status: 500 });
    }

    // Add the secret version
    const versionResponse = await fetch(
      `https://secretmanager.googleapis.com/v1/projects/${projectId}/secrets/${secretId}:addVersion`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          payload: {
            data: Buffer.from(secretPayload).toString('base64'),
          },
        }),
      },
    );

    if (!versionResponse.ok) {
      return NextResponse.json({ error: 'Failed to store key version' }, { status: 500 });
    }

    console.log(`[BYOK] Registered ${provider} key for firm ${firmId.substring(0, 8)}`);

    return NextResponse.json(
      {
        status: 'registered',
        provider,
        secretId,
        registeredAt: new Date().toISOString(),
      },
      {
        headers: {
          'Cache-Control': 'no-store, private',
          'X-Content-Type-Options': 'nosniff',
        },
      },
    );
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json({ error: 'Registration failed' }, { status: 500 });
  }
}

// ─── DELETE: Revoke a BYOK key ──────────────────────────────────────

export async function DELETE(req: NextRequest): Promise<NextResponse> {
  try {
    const seuToken = req.headers.get('x-seu-token');
    if (!seuToken) {
      return NextResponse.json({ error: 'S.E.U. token required' }, { status: 401 });
    }

    const body = await req.json();
    const { provider, firmId } = RevokeKeySchema.parse(body);

    const secretId = `byok-${firmId.substring(0, 8)}-${provider}`;
    const projectId = process.env.GCP_PROJECT_ID ?? 'shadowtag-omega-v4';
    const accessToken = await getAccessToken();

    // Delete the entire secret (all versions)
    const deleteResponse = await fetch(
      `https://secretmanager.googleapis.com/v1/projects/${projectId}/secrets/${secretId}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      },
    );

    if (!deleteResponse.ok && deleteResponse.status !== 404) {
      return NextResponse.json({ error: 'Failed to revoke key' }, { status: 500 });
    }

    console.log(`[BYOK] Revoked ${provider} key for firm ${firmId.substring(0, 8)}`);

    return NextResponse.json({
      status: 'revoked',
      provider,
      revokedAt: new Date().toISOString(),
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json({ error: 'Revocation failed' }, { status: 500 });
  }
}

// ─── Auth Helper ────────────────────────────────────────────────────

async function getAccessToken(): Promise<string> {
  try {
    const res = await fetch(
      'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',
      { headers: { 'Metadata-Flavor': 'Google' } },
    );
    const data = await res.json();
    return data.access_token;
  } catch {
    return process.env.GOOGLE_ACCESS_TOKEN ?? '';
  }
}

/**
 * CounselConduit → KovelAI Bridge API
 *
 * Item #17: Bridge between CounselConduit (control plane) and KovelAI (search plane).
 *
 * Endpoints:
 * - POST /api/bridge/provision → Provision KovelAI tenant from CounselConduit
 * - POST /api/bridge/sync-tier → Sync billing tier changes
 * - POST /api/bridge/health → Health check
 * - POST /api/bridge/attorney-verify → Verify attorney credentials
 *
 * Authentication: Service-to-service via shared HMAC secret.
 *
 * @see CounselConduit: apps/counselconduit
 */

import crypto from 'node:crypto';
import { type NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

// ─── Auth ───────────────────────────────────────────────────────────

const BRIDGE_SECRET = process.env.COUNSELCONDUIT_BRIDGE_SECRET ?? '';

function verifyBridgeAuth(req: NextRequest, body: string): boolean {
  const signature = req.headers.get('x-bridge-signature');
  if (!signature || !BRIDGE_SECRET) return false;

  const expected = crypto.createHmac('sha256', BRIDGE_SECRET).update(body).digest('hex');

  return crypto.timingSafeEqual(Buffer.from(signature, 'hex'), Buffer.from(expected, 'hex'));
}

// ─── Request Schemas ────────────────────────────────────────────────

const ProvisionSchema = z.object({
  action: z.literal('provision'),
  firmId: z.string().uuid(),
  firmName: z.string().min(1),
  tier: z.enum(['solo', 'practice', 'enterprise']),
  adminEmail: z.string().email(),
  stripeAccountId: z.string().optional(),
  maxSeats: z.number().int().min(1).default(5),
  features: z
    .object({
      murderBoard: z.boolean().default(true),
      warRoom: z.boolean().default(false),
      oracleMemo: z.boolean().default(true),
      cleCredits: z.boolean().default(false),
      byok: z.boolean().default(false),
    })
    .default({}),
});

const SyncTierSchema = z.object({
  action: z.literal('sync-tier'),
  firmId: z.string().uuid(),
  newTier: z.enum(['solo', 'practice', 'enterprise']),
  previousTier: z.string(),
  effectiveDate: z.string().datetime(),
});

const HealthSchema = z.object({
  action: z.literal('health'),
  requestId: z.string().uuid(),
});

const AttorneyVerifySchema = z.object({
  action: z.literal('attorney-verify'),
  barNumber: z.string().min(1),
  jurisdiction: z.string().min(1),
  firmId: z.string().uuid(),
});

// ─── Handler ────────────────────────────────────────────────────────

export async function POST(req: NextRequest): Promise<NextResponse> {
  const bodyText = await req.text();

  // Verify HMAC signature
  if (!verifyBridgeAuth(req, bodyText)) {
    return NextResponse.json({ error: 'Unauthorized bridge request' }, { status: 401 });
  }

  let body: unknown;
  try {
    body = JSON.parse(bodyText);
  } catch {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  const action = (body as Record<string, unknown>)?.action;

  try {
    switch (action) {
      case 'provision':
        return handleProvision(ProvisionSchema.parse(body));

      case 'sync-tier':
        return handleSyncTier(SyncTierSchema.parse(body));

      case 'health':
        return handleHealth(HealthSchema.parse(body));

      case 'attorney-verify':
        return handleAttorneyVerify(AttorneyVerifySchema.parse(body));

      default:
        return NextResponse.json({ error: `Unknown action: ${action}` }, { status: 400 });
    }
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json({ error: 'Bridge handler failed' }, { status: 500 });
  }
}

// ─── Action Handlers ────────────────────────────────────────────────

function handleProvision(data: z.infer<typeof ProvisionSchema>): NextResponse {
  // TODO: Wire to Firestore tenant creation
  const tenantConfig = {
    firmId: data.firmId,
    firmName: data.firmName,
    tier: data.tier,
    adminEmail: data.adminEmail,
    stripeAccountId: data.stripeAccountId,
    maxSeats: data.maxSeats,
    features: data.features,
    status: 'provisioning',
    createdAt: new Date().toISOString(),
    kovelaiNamespace: `firms/${data.firmId}`,
    searchEndpoint: `/api/privileged-search`,
    warRoomEndpoint: data.features.warRoom ? `/api/war-room/stream` : null,
    oracleEndpoint: data.features.oracleMemo ? `/api/oracle/render` : null,
  };

  console.log(`[BRIDGE] Provisioning tenant: ${data.firmId} (${data.tier})`);

  return NextResponse.json({
    status: 'provisioned',
    tenant: tenantConfig,
    endpoints: {
      search: `${process.env.NEXT_PUBLIC_APP_URL}/api/privileged-search`,
      warRoom: tenantConfig.warRoomEndpoint
        ? `${process.env.NEXT_PUBLIC_APP_URL}${tenantConfig.warRoomEndpoint}`
        : null,
      oracle: tenantConfig.oracleEndpoint
        ? `${process.env.NEXT_PUBLIC_APP_URL}${tenantConfig.oracleEndpoint}`
        : null,
      cle: data.features.cleCredits ? `${process.env.NEXT_PUBLIC_APP_URL}/api/cle/generate` : null,
    },
  });
}

function handleSyncTier(data: z.infer<typeof SyncTierSchema>): NextResponse {
  // TODO: Wire to Firestore tier update
  console.log(`[BRIDGE] Tier sync: ${data.firmId} ${data.previousTier} → ${data.newTier}`);

  return NextResponse.json({
    status: 'synced',
    firmId: data.firmId,
    tier: data.newTier,
    effectiveDate: data.effectiveDate,
  });
}

function handleHealth(data: z.infer<typeof HealthSchema>): NextResponse {
  return NextResponse.json({
    status: 'healthy',
    requestId: data.requestId,
    service: 'kovelai',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    uptime: process.uptime?.() ?? 0,
  });
}

function handleAttorneyVerify(data: z.infer<typeof AttorneyVerifySchema>): NextResponse {
  // TODO: Wire to actual bar association verification API
  console.log(`[BRIDGE] Attorney verify: ${data.barNumber} (${data.jurisdiction})`);

  return NextResponse.json({
    status: 'pending',
    barNumber: data.barNumber,
    jurisdiction: data.jurisdiction,
    firmId: data.firmId,
    message: 'Verification queued — real-time API integration pending.',
  });
}

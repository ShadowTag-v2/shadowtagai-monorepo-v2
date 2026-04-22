/**
 * S.E.U. Token Minting Endpoint
 *
 * Mints sandbox-bound, ephemeral, user-billed proxy tokens
 * for client-facing research sessions.
 *
 * Nag Protocol #8: Implement S.E.U. token minting endpoint
 */
import { NextResponse, type NextRequest } from 'next/server';
import { z } from 'zod';
import { mintSEUProxyToken } from '@/lib/security/seu-token-manager';

const MintRequestSchema = z.object({
  sandboxId: z.string().min(1),
  sandboxIp: z.string().ip(),
  firmId: z.string().uuid(),
  tierId: z.string().optional(),
  clientState: z.enum(['PROSPECTIVE', 'RETAINED', 'EVAPORATING']).optional(),
});

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    // TODO: Validate server-to-server auth (internal only)
    const apiKey = req.headers.get('x-internal-api-key');
    if (apiKey !== process.env.INTERNAL_API_KEY) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await req.json();
    const parsed = MintRequestSchema.parse(body);

    const token = mintSEUProxyToken(
      parsed.sandboxId,
      parsed.sandboxIp,
      parsed.firmId,
      parsed.tierId,
      parsed.clientState,
    );

    return NextResponse.json({
      token,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      sandboxId: parsed.sandboxId,
      firmId: parsed.firmId,
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json(
      { error: 'Token minting failed' },
      { status: 500 },
    );
  }
}

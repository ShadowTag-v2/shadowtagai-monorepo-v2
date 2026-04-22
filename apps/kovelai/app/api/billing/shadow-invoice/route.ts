/**
 * Shadow Invoice Auto-Drafting for Clio Integration
 *
 * When the Murder Board pipeline completes, automatically drafts
 * a time entry + invoice in the lawyer's Clio account based on
 * the work performed by the AI triage system.
 *
 * Nag Protocol #11: Shadow Invoice auto-draft for Clio
 */
import { NextResponse, type NextRequest } from 'next/server';
import { z } from 'zod';
import { AntigravityMCPClient } from '@/lib/mcp/antigravity-client';

const ShadowInvoiceSchema = z.object({
  firmId: z.string().uuid(),
  matterId: z.string().min(1),
  clientId: z.string().uuid(),
  description: z.string().min(1).max(2000),
  durationMinutes: z.number().min(1).max(480),
  activityType: z.enum([
    'INITIAL_CONSULTATION',
    'CASE_EVALUATION',
    'CONFLICT_CHECK',
    'DOCUMENT_REVIEW',
    'LEGAL_RESEARCH',
    'ORACLE_MEMO',
  ]),
  billableRate: z.number().min(0),
  isBillable: z.boolean().default(true),
});

interface ClioTimeEntry {
  type: string;
  date: string;
  quantity: number;
  total: number;
  note: string;
  activity_description: { id: number };
  matter: { id: number };
  user: { id: number };
}

const ACTIVITY_ID_MAP: Record<string, number> = {
  INITIAL_CONSULTATION: 101,
  CASE_EVALUATION: 102,
  CONFLICT_CHECK: 103,
  DOCUMENT_REVIEW: 104,
  LEGAL_RESEARCH: 105,
  ORACLE_MEMO: 106,
};

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const body = await req.json();
    const parsed = ShadowInvoiceSchema.parse(body);

    // Build the Clio time entry via Antigravity MCP (risk-checked)
    const clioMcpUrl = process.env.CLIO_MCP_URL;
    if (!clioMcpUrl) {
      return NextResponse.json(
        { error: 'Clio MCP not configured' },
        { status: 503 },
      );
    }

    const mcpClient = new AntigravityMCPClient(clioMcpUrl, 'shadow-invoice');

    const hours = parsed.durationMinutes / 60;
    const total = hours * parsed.billableRate;

    const timeEntry: ClioTimeEntry = {
      type: 'TimeEntry',
      date: new Date().toISOString().split('T')[0],
      quantity: hours,
      total,
      note: `[AI-ASSISTED] ${parsed.description}`,
      activity_description: {
        id: ACTIVITY_ID_MAP[parsed.activityType] ?? 100,
      },
      matter: { id: parseInt(parsed.matterId, 10) },
      user: { id: 0 }, // Resolved by Clio from firm context
    };

    // Route through Antigravity interceptor (Tier 2: MITIGATE)
    const result = await mcpClient.callTool('clio_draft_time_entry', {
      timeEntry,
      firmId: parsed.firmId,
      isDraft: true, // Always draft — never auto-submit
    });

    return NextResponse.json({
      status: 'DRAFTED',
      timeEntry: {
        hours: hours.toFixed(2),
        total: total.toFixed(2),
        activityType: parsed.activityType,
        matterId: parsed.matterId,
      },
      clioResponse: result,
      note: 'Shadow invoice drafted. Lawyer must approve before submission.',
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json(
      { error: 'Shadow invoice draft failed' },
      { status: 500 },
    );
  }
}

import { NextResponse } from 'next/server';

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://localhost:8080';

// Handle POST to create/start an orchestration session
export async function POST(req: Request) {
  try {
    const body = await req.json();

    // Connect to the Python orchestrator
    const res = await fetch(`${ORCHESTRATOR_URL}/api/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description: body.description || 'Analyze video' }),
    });

    if (!res.ok) {
      throw new Error(`Orchestrator returned ${res.status}`);
    }

    const data = await res.json();

    return NextResponse.json({
      status: 'created',
      sessionId: data.task_id,
      message: 'Backend Bridge API connected to python orchestrator.',
    });
  } catch (_error) {
    // console.error('Failed to initiate orchestration:', error);
    return NextResponse.json({ error: 'Failed to initiate orchestration' }, { status: 500 });
  }
}

// Handle GET for basic status or future polling fallback
export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const sessionId = searchParams.get('sessionId');

  if (!sessionId) {
    return NextResponse.json({ error: 'Missing sessionId' }, { status: 400 });
  }

  try {
    // Pass-through stream from python backend
    const res = await fetch(`${ORCHESTRATOR_URL}/api/tasks/${sessionId}/stream`);

    return new Response(res.body || undefined, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-transform',
        Connection: 'keep-alive',
      },
    });
  } catch (error) {
    void error;
    // console.error('SSE Stream error:', error);
    return NextResponse.json({ error: 'Failed to stream from orchestrator' }, { status: 500 });
  }
}

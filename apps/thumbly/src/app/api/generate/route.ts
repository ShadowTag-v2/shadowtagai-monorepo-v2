import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co',
  process.env.SUPABASE_SERVICE_ROLE_KEY || 'placeholder',
);

export async function POST(req: Request) {
  try {
    const { prompt, style: _style, userId } = await req.json();

    if (!userId || !prompt) {
      return NextResponse.json(
        { error: 'Missing required payload (userId, prompt)' },
        { status: 400 },
      );
    }

    // 1. Strict Payment Lifecycle Doctrine: Entitlement Check
    const { data: userRecord, error: fetchError } = await supabase
      .from('users')
      .select('credits')
      .eq('id', userId)
      .single();

    if (fetchError || !userRecord) {
      return NextResponse.json({ error: 'Failed to verify ledger entitlement.' }, { status: 403 });
    }

    if (userRecord.credits <= 0) {
      return NextResponse.json(
        { error: 'Insufficient credits. Top up required.' },
        { status: 402 },
      );
    }

    // 2. Inference Invocation (Placeholder for actual API/Replicate bridge)
    // Here we would call Replicate, fal.ai, or the local NPU bridge.
    // Example: const imageUrl = await Replicate.run(...)
    const generatedImagePath =
      'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop';

    // Simulate inference latency
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // 3. Ledger Debit Operation (Deterministic subtract)
    const { error: debitError } = await supabase.rpc('decrement_credits', {
      user_id: userId,
      amount: 1,
    });

    if (debitError) {
    }

    // Return the generated asset URI
    return NextResponse.json(
      {
        success: true,
        imageUrl: generatedImagePath,
        remainingCredits: userRecord.credits - 1,
      },
      { status: 200 },
    );
  } catch (err: unknown) {
    return NextResponse.json(
      { error: `Generation Engine Fatal Error: ${err.message}` },
      { status: 500 },
    );
  }
}

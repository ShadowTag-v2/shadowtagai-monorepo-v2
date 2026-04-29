'use client';

import { loadStripe } from '@stripe/stripe-js';
import { useState } from 'react';

// Initialize Stripe (Public Key is safe here)
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

export default function ReactorCore() {
  const [loading, setLoading] = useState(false);

  const handleIgnition = async () => {
    setLoading(true);
    try {
      const stripe = await stripePromise;
      if (!stripe) throw new Error('Stripe failed to initialize.');

      // Call your secure backend (see Step 3)
      const response = await fetch('/api/ignite-reactor', { method: 'POST' });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const session = await response.json();

      // Redirect to "Gucci" Checkout
      const result = await stripe.redirectToCheckout({ sessionId: session.id });

      if (result.error) {
        console.error(result.error.message);
      }
    } catch (error) {
      console.error('Ignition failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative group w-full max-w-md mx-auto">
      {/* The Holographic Glow */}
      <div className="absolute -inset-0.5 bg-gradient-to-r from-brand to-purple-600 rounded-xl blur opacity-20 group-hover:opacity-75 transition duration-1000"></div>

      <div className="relative bg-surface border border-tension p-8 rounded-xl overflow-hidden">
        {/* Ambient Background */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-brand/5 blur-[80px] rounded-full pointer-events-none" />

        <div className="relative z-10">
          <div className="flex justify-between items-start mb-6">
            <h3 className="text-starlight font-mono text-lg tracking-widest">
              &gt; SOVEREIGN_NODE
            </h3>
            <div className="px-2 py-1 border border-tension bg-void rounded">
              <span className="text-burn font-mono text-[10px] animate-pulse">● SYSTEM_READY</span>
            </div>
          </div>

          <div className="mb-8">
            <div className="flex items-baseline">
              <span className="text-5xl font-mono text-starlight tracking-tighter">$49</span>
              <span className="ml-2 text-ghost font-mono text-xs uppercase">/ Epoch</span>
            </div>
            <p className="mt-4 text-gray-400 text-sm font-light leading-relaxed">
              Allocates 100 Compute Credits. Full access to Cor.Claude_Code_6 reasoning engine.
              <span className="text-brand block mt-1">Provenance: Dataform Strict Mode.</span>
            </p>
          </div>

          <button
            onClick={handleIgnition}
            disabled={loading}
            className="w-full py-4 bg-starlight hover:bg-white text-void font-mono font-bold tracking-widest uppercase rounded transition-all transform active:scale-[0.98] shadow-[0_0_20px_rgba(255,255,255,0.2)] hover:shadow-[0_0_30px_rgba(110,86,207,0.4)]"
          >
            {loading ? 'INITIALIZING...' : '[ IGNITE REACTOR ]'}
          </button>

          <div className="mt-6 pt-6 border-t border-tension flex justify-between text-[10px] font-mono text-gray-500 uppercase">
            <span>Security: AES-256</span>
            <span>Arch: Vertex_Agent</span>
          </div>
        </div>
      </div>
    </div>
  );
}

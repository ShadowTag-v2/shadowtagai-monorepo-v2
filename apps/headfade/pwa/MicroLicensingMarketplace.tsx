'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';

interface Workflow {
  id: string;
  title: string;
  creator: string;
  price: number;
  thumbnail: string;
  remixCount: number;
}

export default function MicroLicensingMarketplace() {
  const [workflows, setWorkflows] = useState<Workflow[]>([
    {
      id: 'wf-001',
      title: 'Cyberpunk Neon Dreams',
      creator: '@neonvoid_ai',
      price: 2.99,
      thumbnail: 'https://picsum.photos/id/1015/300/200',
      remixCount: 1247
    },
    {
      id: 'wf-002',
      title: 'Surreal Floating Islands',
      creator: '@dreamweave',
      price: 2.99,
      thumbnail: 'https://picsum.photos/id/102/300/200',
      remixCount: 892
    }
  ]);

  const purchaseMutation = useMutation({
    mutationFn: async (workflowId: string) => {
      const res = await fetch('/api/mcp/purchase_workflow_license', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ videoId: workflowId, agentWalletToken: 'agnt_demo_123' })
      });
      return res.json();
    }
  });

  const handlePurchase = (workflow: Workflow) => {
    purchaseMutation.mutate(workflow.id, {
      onSuccess: () => {
        alert(`✅ License purchased! Workflow "${workflow.title}" unlocked.`);
      }
    });
  };

  return (
    <div className="max-w-6xl mx-auto p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">Workflow Marketplace</h1>
        <p className="text-zinc-400">Buy, remix, and resell ComfyUI workflows • $2.99 per license</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workflows.map((workflow) => (
          <div key={workflow.id} className="bg-zinc-900 rounded-2xl overflow-hidden border border-zinc-800 hover:border-zinc-700 transition-all">
            <img 
              src={workflow.thumbnail} 
              alt={workflow.title}
              className="w-full h-48 object-cover"
            />
            
            <div className="p-5">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="font-semibold text-white text-lg">{workflow.title}</h3>
                  <p className="text-sm text-zinc-500">{workflow.creator}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-emerald-400">${workflow.price}</div>
                </div>
              </div>

              <div className="flex items-center justify-between text-sm text-zinc-400 mb-4">
                <span>{workflow.remixCount.toLocaleString()} remixes</span>
                <span className="px-2 py-0.5 bg-zinc-800 rounded">ComfyUI</span>
              </div>

              <button
                onClick={() => handlePurchase(workflow)}
                disabled={purchaseMutation.isPending}
                className="w-full py-3 bg-white text-black font-semibold rounded-xl hover:bg-zinc-200 transition disabled:opacity-50"
              >
                {purchaseMutation.isPending ? 'Processing...' : 'Buy License • $2.99'}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 text-center text-xs text-zinc-500">
        20% platform fee • Instant A2A delivery • Full remix rights included
      </div>
    </div>
  );
}
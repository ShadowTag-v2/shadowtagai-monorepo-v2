'use client';

import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

interface RemixNode {
  id: string;
  label: string;
  model: string;
  hdi: number;
  children?: RemixNode[];
}

export default function RemixTreeVisualizer({ videoId }: { videoId: string }) {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  const { data: tree, isLoading } = useQuery({
    queryKey: ['remixTree', videoId],
    queryFn: async () => {
      const res = await fetch(`/api/v2/remix-lineage?videoId=${videoId}&depth=5`);
      return res.json();
    },
  });

  const toggleNode = (id: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedNodes(newExpanded);
  };

  if (isLoading) return <div className="p-8 text-center">Loading Remix Tree...</div>;

  return (
    <div className="bg-zinc-950 p-8 rounded-3xl border border-zinc-800">
      <h2 className="text-3xl font-bold text-white mb-6">Remix Tree Visualizer</h2>

      <div className="space-y-2 font-mono text-sm">
        {tree?.lineage?.map((node: RemixNode, index: number) => (
          <div key={index} className="pl-4 border-l border-zinc-700">
            <div
              onClick={() => toggleNode(node.id)}
              className="flex items-center gap-3 cursor-pointer hover:bg-zinc-900 p-2 rounded"
            >
              <span className="text-emerald-400">↳</span>
              <span className="text-white font-semibold">{node.label}</span>
              <span className="text-xs px-2 py-0.5 bg-zinc-800 rounded text-zinc-400">
                {node.model}
              </span>
              <span className="text-rose-400">HDI: {node.hdi}%</span>
            </div>

            {expandedNodes.has(node.id) && node.children && (
              <div className="ml-8 mt-1 space-y-1">
                {node.children.map((child, i) => (
                  <div key={i} className="text-zinc-400 pl-6 border-l border-zinc-800">
                    {child.label} ({child.model})
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-8 text-xs text-zinc-500">
        Cryptographically signed • Immutable • Powered by HeadFade V2
      </div>
    </div>
  );
}
```

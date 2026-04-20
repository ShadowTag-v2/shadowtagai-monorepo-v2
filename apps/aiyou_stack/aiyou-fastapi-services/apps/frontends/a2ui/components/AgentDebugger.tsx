'use client';

import { useCopilotContext } from '@copilotkit/react-core'; // v1.x hook
import React, { useEffect, useState } from 'react';

export function AgentDebugger() {
  const [events, setEvents] = useState<any[]>([]);
  // In newer CopilotKit versions, we can hook into the context or specific agent state.
  // For this demo, we simulate the 'useAgent' subscription described in the article if available,
  // or fall back to context monitoring.

  // Placeholder: Implementing the event stream listener pattern from the article.
  // Real implementation depends on the exact version of @copilotkit/react-core installed.

  return (
    <div className="flex flex-col gap-2 h-96 overflow-y-auto bg-slate-950 text-green-500 p-4 rounded border border-green-800 font-mono text-xs">
      <div className="flex justify-between border-b border-green-800 pb-2 mb-2">
        <span className="font-bold">MATRIX DEBUGGER (AG-UI STREAM)</span>
        <span className="animate-pulse">● LIVE</span>
      </div>
      {events.length === 0 && <div className="text-gray-500 italic">Waiting for signal...</div>}
      {events.map((event, idx) => (
        <GenericEventCard key={idx} event={event} />
      ))}
    </div>
  );
}

function GenericEventCard({ event }: { event: unknown }) {
  const { type, agentId } = event;
  const timestamp = new Date().toISOString();

  const getTypeColor = (type: string) => {
    if (type.includes('TEXT')) return 'text-blue-400';
    if (type.includes('TOOL')) return 'text-purple-400';
    if (type.includes('STATE')) return 'text-yellow-400';
    return 'text-gray-300';
  };

  return (
    <div className="border border-green-900/50 rounded p-2 bg-slate-900/50">
      <div className="flex justify-between mb-1">
        <span className={`font-bold ${getTypeColor(type)}`}>{type}</span>
        <span className="text-[10px] text-green-700">{agentId}</span>
      </div>
      <div className="text-green-300/80 break-all">
        {/* Simple rendering logic */}
        <pre>{JSON.stringify(event, null, 2)}</pre>
      </div>
    </div>
  );
}

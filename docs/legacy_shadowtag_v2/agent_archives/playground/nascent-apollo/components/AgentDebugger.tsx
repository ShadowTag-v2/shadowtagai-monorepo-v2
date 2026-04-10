"use client";

import React, { useState, useEffect } from "react";
// MOCK: In real usage, import from @copilotkit/react
// import { useAgent } from "@copilotkit/react";

// Mocking types for visualization
interface AgentEvent {
  type: string;
  agentId: string;
  delta?: string;
  timestamp: number;
  [key: string]: any;
}

export function AgentDebugger() {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  
  // MOCK: Simulating event stream for Gemini 3.0 Agent
  useEffect(() => {
    const mockInterval = setInterval(() => {
      const newEvent: AgentEvent = {
        type: Math.random() > 0.5 ? "TEXT_MESSAGE_CONTENT" : "TOOL_CALL_ARGS",
        agentId: "gemini-3.0-flash-agent",
        delta: Math.random() > 0.5 ? "Thinking..." : '{"arg": "value"}',
        timestamp: Date.now()
      };
      setEvents((prev) => [newEvent, ...prev]);
    }, 3000);

    return () => clearInterval(mockInterval);
  }, []);

  const getTypeColor = (type: string) => {
    if (type === "TEXT_MESSAGE_CONTENT") return "text-blue-500";
    if (type === "TOOL_CALL_ARGS") return "text-purple-600";
    return "text-green-500";
  };

  return (
      <div className="flex flex-col gap-2 h-96 overflow-y-auto bg-slate-50 p-4 rounded border">
        <h3 className="text-xs font-bold text-gray-400 uppercase">AG-UI Event Stream (Gemini 3.0)</h3>
        {events.map((event, idx) => (
          <div key={idx} className="border border-gray-200 rounded p-3 text-sm bg-white font-mono">
             <div className="flex justify-between mb-2">
                <span className={`font-bold uppercase ${getTypeColor(event.type)}`}>{event.type}</span>
                <span className="text-xs text-gray-500">{event.agentId}</span>
             </div>
             <div className="text-xs text-gray-700">
               {event.type === "TEXT_MESSAGE_CONTENT" && <div><span className="font-bold text-blue-400">Delta: </span>"{event.delta}"</div>}
               {event.type === "TOOL_CALL_ARGS" && <div><span className="font-bold text-purple-600">Arg Delta: </span>{event.delta}</div>}
             </div>
          </div>
        ))}
      </div>
  );
}

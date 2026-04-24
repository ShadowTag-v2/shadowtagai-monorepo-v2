import { useAgent } from '@copilotkit/react-core';
import { useEffect, useState } from 'react';

// Define a type for agent events to clear the 'any' typescript warning
export interface AgentEvent {
  type: string;
  agentId?: string;
  delta?: string;
  timestamp?: number;
  _receivedAt?: number;
  name?: string;
  payload?: any;
  [key: string]: any;
}

// Visual aid for different AG-UI components
const getTypeColor = (type: string) => {
  if (type === 'TEXT_MESSAGE_CONTENT' || type === 'RUN_STARTED') return 'text-blue-500';
  if (type.includes('TOOL')) return 'text-purple-500';
  if (type === 'A2UI_PAYLOAD') return 'text-green-500';
  return 'text-gray-500';
};

function GenericEventCard({ event }: { event: AgentEvent }) {
  // Extract flat AG-UI keys native to the useAgent hook stream
  const { type, agentId, delta } = event;

  return (
    <div className="border border-gray-800 rounded p-3 text-sm bg-black/90 font-mono shadow-lg mb-2 text-green-400">
      {/* Event Header */}
      <div className="flex justify-between mb-2">
        <span className={`font-bold uppercase ${getTypeColor(type)}`}>{type}</span>
        <span className="text-xs text-gray-500">{agentId}</span>
      </div>

      <div className="text-xs overflow-x-auto break-all">
        {/* Text Streaming */}
        {type === 'TEXT_MESSAGE_CONTENT' && (
          <div>
            <span className="font-bold text-blue-400">Delta: </span>"{delta}"
          </div>
        )}

        {/* Tool Args */}
        {(type === 'TOOL_CALL_ARGS' || type === 'TOOL_CALL_START') && (
          <div>
            <span className="font-bold text-purple-600">Tool Trigger: </span>
            {event.name || delta}
          </div>
        )}

        {/* Generative A2UI Payload */}
        {type === 'A2UI_PAYLOAD' && (
          <div className="border-l-2 border-green-500 pl-2 mt-2">
            <span className="font-bold text-green-500">Component Matrix Triggered.</span>
            <br />
            Render Inject: {event.payload?.type}
          </div>
        )}

        {/* Raw JSON inspection toggle */}
        <details className="mt-2 text-[10px] text-gray-400">
          <summary className="cursor-pointer hover:text-white transition-colors">
            Raw Memory Tensor
          </summary>
          <pre className="bg-gray-900 p-2 mt-1 rounded text-orange-400">
            {JSON.stringify(event, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}

export function AgentDebugger() {
  const [events, setEvents] = useState<AgentEvent[]>([]);

  // Hook natively into the Cor.Firebase endpoint (or ADK wrapper)
  // Ensure the top-level <CopilotKit> context has runtimeUrl pointing to the gateway.
  const { agent } = useAgent({
    agentId: 'data_science_agent', // Configured to match BioAgent router
  });

  useEffect(() => {
    if (agent) {
      const subscriber = {
        onEvent: ({ event }: { event: AgentEvent }) => {
          const enrichedEvent = {
            ...event,
            _receivedAt: Date.now(),
          };
          // Prepend so the newest event is at top
          setEvents((prev) => [enrichedEvent, ...prev]);
        },
      };

      const subscription = agent.subscribe(subscriber);
      return () => subscription.unsubscribe();
    }
  }, [agent]);

  return (
    <div className="flex flex-col gap-2 h-[500px] overflow-y-auto bg-gray-950 p-4 rounded-xl border border-gray-800">
      <h3 className="text-white text-xs tracking-widest font-bold mb-4 border-b border-gray-800 pb-2">
        [[ AG-UI MATRIX STREAM ]]
      </h3>
      {events.length === 0 && (
        <p className="text-gray-600 text-xs italic">Awaiting Agent Telemetry...</p>
      )}
      {events.map((event, idx) => {
        // Fallback to purely unique ID if timeline timestamps perfectly overlap
        const uniqueKey = event._receivedAt ? `${event._receivedAt}-${idx}` : idx;
        return <GenericEventCard key={uniqueKey} event={event} />;
      })}
    </div>
  );
}

import React, { useEffect, useState } from 'react';

interface PipelineResult {
    layerId: string;
    failureCount: number;
}

export function SandTable() {
  const [telemetry, setTelemetry] = useState<PipelineResult[]>([]);
  const [loading, setLoading] = useState(true);

  // Demonstrated Pipeline execution leveraging the Web SDK update for Firestore
  useEffect(() => {
    async function fetchComplianceTelemetry() {
        setLoading(true);
        try {
            // In the physical edge implementation, we execute:
            /*
            const swarmTelemetry = await db.pipeline()
                .collection("whiteboard_issues")
                .where(field("status").equal("KICKBACK_LOOP"))
                .unnest(field("violated_layers").as("layerId"))
                .aggregate({
                  accumulators: [countAll().as("failureCount")],
                  groups: ["layerId"]
                })
                .sort(field("failureCount").descending())
                .execute();
            */
            
            // Natively reading the Swarm A2UI stream instead of mock aggregation
            const response = await fetch("http://127.0.0.1:8002/api/v1/agents/stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    workspace_id: "local",
                    agent_id: "cor-cursor-dev-01",
                    message: "Deploy Matrix A2UI Dashboard"
                })
            });

            if (!response.body) throw new Error("A2UI Matrix failed to return readable stream.");
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.type === "A2UI_PAYLOAD" && data.payload.type === "SandTable") {
                                setTelemetry(data.payload.data.telemetry);
                                setLoading(false);
                            }
                        } catch (e) {
                            // Mute parse errors from incomplete chunks
                        }
                    }
                }
            }
            
        } catch (e) {
            console.error("Pipeline aggregation failure:", e);
            setLoading(false);
        }
    }
    
    fetchComplianceTelemetry();
  }, []);

  return (
    <div className="bg-gray-950 border border-red-900/30 rounded-xl p-4 mt-6 shadow-2xl">
      <h3 className="text-red-500/80 text-xs tracking-widest font-bold mb-4 border-b border-gray-800 pb-2 flex justify-between">
         <span>[[ ATP 5-19 SHIELD : PIPELINE TELEMETRY ]]</span>
         <span className="text-[10px] bg-red-950 px-2 rounded">LIVE</span>
      </h3>
      
      {loading ? (
          <div className="text-gray-500 text-xs font-mono animate-pulse">Aggregating Swarm Telemetry...</div>
      ) : (
          <div className="flex flex-col gap-2">
             {telemetry.map((t, idx) => (
                 <div key={idx} className="flex justify-between items-center text-xs text-red-400 bg-red-950/20 p-2 rounded border border-red-900/50 opacity-90 hover:opacity-100 transition-opacity">
                    <span className="font-mono">{t.layerId}</span>
                    <span className="font-bold bg-red-900/40 px-2 py-1 rounded shadow-inner tracking-widest text-[10px]">
                        {t.failureCount} FAILURES MITIGATED
                    </span>
                 </div>
             ))}
          </div>
      )}
    </div>
  );
}

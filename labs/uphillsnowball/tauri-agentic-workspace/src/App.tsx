import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { CopilotKit } from "@copilotkit/react-core";
import { AgentDebugger } from "./components/AgentDebugger";
import { SandTable } from "./components/SandTable";
import "./App.css";

interface StreamPayload {
  log: string | null;
  node: string | null;
  status: string | null;
  result: string | null;
}

interface LogEntry {
  timestamp: string;
  message: string;
  type: "info" | "error" | "success" | "node";
}

function App() {
  const [task, setTask] = useState("");
  const [domain, setDomain] = useState("");
  const [useAne, setUseAne] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);

  useEffect(() => {
    let unlisten: () => void;
    
    async function setupListener() {
      unlisten = await listen<StreamPayload>("agent_stream", (event) => {
        const payload: StreamPayload = event.payload;
        
        let type: "info" | "error" | "success" | "node" = "info";
        if (payload.status === "error") type = "error";
        if (payload.status === "success") type = "success";
        if (payload.node) type = "node";
        
        if (payload.log) {
          setLogs(prev => [...prev, {
            timestamp: new Date().toLocaleTimeString(),
            message: payload.log || "",
            type
          }]);
        }
        
        if (payload.status === "success" || payload.status === "error") {
          setLoading(false);
        }
      });
    }
    setupListener();
    return () => { if (unlisten) unlisten(); };
  }, []);

  async function handleDispatch(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setLogs([{
      timestamp: new Date().toLocaleTimeString(),
      message: ">>> LAUNCHING SWARM. RUST ENFORCER VERIFYING PAYLOAD...",
      type: "info"
    }]);
    
    try {
      // THE BRAKES: This call routes physically through Rust before hitting the Python engine
      await invoke("invoke_agent", { 
        task: task,
        targetDomain: domain ? domain : null,
        useAne: useAne
      });
    } catch (err: unknown) {
      // Rust intercepts and throws a string error if the domain is blacklisted
      setLogs(prev => [...prev, {
        timestamp: new Date().toLocaleTimeString(),
        message: String(err),
        type: "error"
      }]);
      setLoading(false);
    }
  }

  return (
    <div className="terminal-container">
      <header className="terminal-header">
        <h1>ShadowTagAi <span>UphillSnowball</span></h1>
        <div className="status-indicators">
          <div className="indicator active">RUST FIREWALL: ON</div>
          <div className="indicator active">TAURI LAYER: ACTIVE</div>
          <div className="indicator active">PYTHON SIDECAR: SSE CONNECTED</div>
        </div>
      </header>
      
      <main className="terminal-main">
        <section className="dispatch-panel">
          <h2>[ NEW MISSION DIRECTIVE ]</h2>
          <form onSubmit={handleDispatch} className="dispatch-form">
            <div className="form-group">
              <label htmlFor="task-input">Objective / Target Query:</label>
              <input
                id="task-input"
                autoComplete="off"
                onChange={(e) => setTask(e.currentTarget.value)}
                placeholder="Extract context metrics from..."
                required
              />
            </div>
            
            <div className="form-group row">
              <div className="input-half">
                <label htmlFor="domain-input">Target Domain (Optional):</label>
                <input
                  id="domain-input"
                  autoComplete="off"
                  onChange={(e) => setDomain(e.currentTarget.value)}
                  placeholder="e.g. competitor.com or restricted.gov"
                />
              </div>
              
              <div className="input-half checkbox">
                <label>
                  <input 
                    type="checkbox" 
                    checked={useAne} 
                    onChange={(e) => setUseAne(e.target.checked)} 
                  />
                  Require Local ANE Zero-Token Inference
                </label>
              </div>
            </div>
            
            <button type="submit" className="dispatch-btn" disabled={loading}>
              {loading ? ">>> EXECUTING..." : "DISPATCH AGENT SWARM"}
            </button>
          </form>
          
          {/* CISO Command Center Pipeline Component */}
          <SandTable />
        </section>

        <section className="telemetry-panel">
          <h2>[ LIVE AG-UI MATRIX STREAM ]</h2>
          <div className="terminal-output">
            <CopilotKit runtimeUrl="http://127.0.0.1:8081/api/v1/agents/stream" agent="data_science_agent">
               <AgentDebugger />
            </CopilotKit>
            
            {loading && (
              <div className="log-entry processing mt-2">
                <span className="timestamp">{new Date().toLocaleTimeString()}</span>
                <span className="message cursor-blink">_</span>
              </div>
            )}
            
            {logs.map((log, i) => (
              <div key={i} className={`log-entry ${log.type}`}>
                <span className="timestamp">{log.timestamp}</span>
                <span className="message">{log.message}</span>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;

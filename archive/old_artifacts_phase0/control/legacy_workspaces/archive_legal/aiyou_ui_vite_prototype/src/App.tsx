import { useState } from "react";
import "./App.css";

interface AgentResponse {
  synthesis: string;
  exhibitsUsed: number;
  metrics: {
    personaId: string;
    cognitiveStrictnessLevel: number;
  };
}

interface Interaction {
  id: string;
  query: string;
  response?: AgentResponse;
  loading: boolean;
  error?: string;
}

function App() {
  const [inputStr, setInputStr] = useState("");
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [activeMetrics, setActiveMetrics] = useState({
    exhibits: 0,
    strictness: 27,
    status: "IDLE",
  });

  const handleSubmit = async () => {
    if (!inputStr.trim()) return;

    const newId = Date.now().toString();
    const newInteraction: Interaction = { id: newId, query: inputStr, loading: true };

    setInteractions((prev) => [...prev, newInteraction]);
    setInputStr("");
    setActiveMetrics((m) => ({ ...m, status: "EXTRACTING (ZERO-DRIFT)" }));

    try {
      // Connect to the ShadowTag-v2 Agent Endpoint
      const apiBase = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
      const res = await fetch(`${apiBase}/api/v1/ShadowTag-v2/agent/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ q: newInteraction.query }),
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error || "Network error");

      setInteractions((prev) =>
        prev.map((i) => (i.id === newId ? { ...i, loading: false, response: data } : i)),
      );

      setActiveMetrics({
        exhibits: data.exhibitsUsed,
        strictness: data.metrics.cognitiveStrictnessLevel,
        status: "SYNTHESIS RENDERED",
      });
    } catch (err: any) {
      setInteractions((prev) =>
        prev.map((i) => (i.id === newId ? { ...i, loading: false, error: err.message } : i)),
      );
      setActiveMetrics((m) => ({ ...m, status: "ERROR" }));
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar Metrics */}
      <aside className="sidebar glass-panel">
        <div className="brand">
          <h1>
            ShadowTag-v2 <span>Core</span>
          </h1>
        </div>

        <div className="metric-group">
          <div className="metric-title">Agentic Routing State</div>

          <div className="metric">
            <span>Status</span>
            <span
              className="val"
              style={{
                color: activeMetrics.status.includes("ERROR") ? "#ff4f4f" : "var(--accent-blue)",
              }}
            >
              {activeMetrics.status}
            </span>
          </div>
          <div className="metric">
            <span>Semantic Extraction</span>
            <span className="val">ZERO-DRIFT</span>
          </div>
          <div className="metric">
            <span>Material Exhibits Active</span>
            <span className="val">{activeMetrics.exhibits} Nodes</span>
          </div>
          <div className="metric">
            <span>Cognitive Constraint</span>
            <span className="val">{activeMetrics.strictness} Years (Legal)</span>
          </div>
          <div className="metric">
            <span>Arbitration Syntax</span>
            <span className="val">Locked</span>
          </div>
        </div>

        <div className="metric-group" style={{ marginTop: "auto" }}>
          <div className="metric-title">Network Identity</div>
          <div className="metric" style={{ fontSize: "0.65rem", color: "var(--text-dim)" }}>
            [ST-V2] Metagraph Connected.
            <br />
            ShadowTag Hash Siloed.
          </div>
        </div>
      </aside>

      {/* Main Terminal Stage */}
      <main className="main-stage glass-panel">
        <div className="terminal-flow">
          {interactions.map((interaction) => (
            <div key={interaction.id} className="interaction animate-in">
              <div className="query-box">{interaction.query}</div>

              {interaction.loading && (
                <div style={{ padding: "16px", color: "var(--accent-gold)", fontSize: "0.85rem" }}>
                  Establishing material facts. Computing deductive synthesis...
                </div>
              )}

              {interaction.error && (
                <div style={{ padding: "16px", color: "#ff4f4f", fontSize: "0.85rem" }}>
                  [System Fault]: {interaction.error}
                </div>
              )}

              {interaction.response && (
                <div
                  style={{
                    marginTop: "16px",
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px",
                  }}
                >
                  <div className="exhibits">
                    <span className="exhibit-title">
                      Material Exhibits ({interaction.response.exhibitsUsed})
                    </span>
                    <div className="exhibit-item">
                      {/* Normally we'd map over snippets here. The backend response abstracts it momentarily. */}
                      [RAG Vector Database accessed. {interaction.response.exhibitsUsed} context
                      nodes returned.]
                    </div>
                  </div>
                  <div className="synthesis">
                    <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", margin: 0 }}>
                      {interaction.response.synthesis}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="input-area">
          <input
            type="text"
            className="styled-input"
            placeholder="Execute protocol query or supply scenario parameters..."
            value={inputStr}
            onChange={(e) => setInputStr(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          />
          <button className="submit-btn" onClick={handleSubmit} disabled={!inputStr.trim()}>
            Transmit
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;

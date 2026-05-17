import type React from "react";
import { useState } from "react";
import "./jules-session.css";

interface JulesSessionControlProps {
  sourceName: string;
  sessionName?: string;
  status?: string;
  onApprovePlan?: (message: string) => void;
  onInteract?: (message: string) => void;
}

export const JulesSessionControl: React.FC<JulesSessionControlProps> = ({
  sourceName,
  sessionName = "Initializing...",
  status = "CONNECTING",
  onApprovePlan,
  onInteract,
}) => {
  const [inputValue, setInputValue] = useState("");

  const isPendingApproval = status === "PENDING_APPROVAL";
  const isActive = status === "ACTIVE" || isPendingApproval;

  const handleInteract = () => {
    if (inputValue.trim() && onInteract) {
      onInteract(inputValue);
      setInputValue("");
    }
  };

  const handleApprove = () => {
    if (onApprovePlan) {
      onApprovePlan(inputValue || "Plan approved via UI");
      setInputValue("");
    }
  };

  return (
    <div className="sovereign-container">
      <div className="sovereign-display">Jules Orchestrator</div>

      <div className="sovereign-card sovereign-glass">
        <div className="sovereign-label">Active Source</div>
        <div style={{ color: "#ffffff", marginBottom: "1.5rem", fontFamily: "monospace" }}>
          {sourceName}
        </div>

        <div className="sovereign-label">Session Status</div>
        <div className="sovereign-active-state">
          <div style={{ display: "flex", alignItems: "center", marginBottom: "0.5rem" }}>
            <span
              className={isActive ? "sovereign-status" : ""}
              style={
                !isActive
                  ? {
                      display: "inline-block",
                      width: "8px",
                      height: "8px",
                      borderRadius: "50%",
                      backgroundColor: "#ffb4ab",
                      marginRight: "0.5rem",
                    }
                  : {}
              }
            ></span>
            <span style={{ color: "#ffffff", fontWeight: 600 }}>{status}</span>
          </div>
          <div style={{ fontSize: "0.875rem", fontFamily: "monospace" }}>{sessionName}</div>
        </div>
      </div>

      <div className="sovereign-card sovereign-glass" style={{ marginTop: "2rem" }}>
        <div className="sovereign-label">Command Interface</div>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Issue command or approval message..."
          style={{
            width: "100%",
            background: "transparent",
            border: "none",
            borderBottom: "1px solid var(--sovereign-outline-variant)",
            color: "#ffffff",
            padding: "0.75rem 0",
            fontFamily: "var(--font-space-grotesk)",
            outline: "none",
            marginBottom: "1.5rem",
          }}
        />

        <div style={{ display: "flex", gap: "1rem" }}>
          <button
            type="button"
            className="sovereign-btn-primary"
            onClick={handleInteract}
            disabled={!isActive}
            style={{ opacity: !isActive ? 0.5 : 1 }}
          >
            Transmit Command
          </button>

          {isPendingApproval && (
            <button type="button" className="sovereign-btn-secondary" onClick={handleApprove}>
              Approve Plan
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

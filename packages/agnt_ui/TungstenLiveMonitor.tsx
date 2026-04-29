import React, { useState, useEffect } from 'react';

/**
 * TungstenLiveMonitor
 * React component for monitoring background tmux sessions (e.g. via Loop Steward).
 * Equivalent to Claude Code's TungstenLiveMonitor.
 */
export const TungstenLiveMonitor: React.FC<{ sessionId: string }> = ({ sessionId }) => {
    const [logs, setLogs] = useState<string[]>([]);
    const [isExpanded, setIsExpanded] = useState(true);

    useEffect(() => {
        // In a real app, this would tail the tmux socket or log file
        const interval = setInterval(() => {
            setLogs(prev => [...prev, `[${new Date().toISOString()}] Background task ping...`]);
        }, 5000);
        return () => clearInterval(interval);
    }, [sessionId]);

    if (!isExpanded) {
        return (
            <div className="tungsten-pill" onClick={() => setIsExpanded(true)}>
                <span>🟢 Background Job {sessionId} Running...</span>
            </div>
        );
    }

    return (
        <div className="tungsten-monitor-panel">
            <div className="header">
                <h3>Tmux Session: {sessionId}</h3>
                <button onClick={() => setIsExpanded(false)}>Minimize</button>
            </div>
            <div className="terminal-output">
                {logs.map((log, i) => <div key={i}>{log}</div>)}
            </div>
        </div>
    );
};

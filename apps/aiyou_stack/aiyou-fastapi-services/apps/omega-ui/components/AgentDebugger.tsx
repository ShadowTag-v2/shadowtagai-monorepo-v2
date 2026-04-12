"use client";

import { CopilotSidebar } from "@copilotkit/react-ui";

export function AgentDebugger() {
  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      <CopilotSidebar
        defaultOpen={true}
        instructions="You are interacting with the Autoresearch Swarm via the Judge 6 Governance Layer."
        labels={{
          title: "Omega UI // Judge 6",
          initial: "Judge 6 Online. How may I assist you, Sovereign?",
        }}
        // Explicitly target the named agent from the backend
        // Note: useCoAgent or actions often auto-bind if only one exists,
        // but 'default' implies a fallback.
        // We will try to rely on the Provider's connection,
        // but if that fails, we might need a workaround.
        // CopilotSidebar doesn't inherently take an 'agent' prop in all versions.
        // Let's assume standard behavior first, but if THIS fails again,
        // we'll patch the backend to alias 'default'.
      />
    </div>
  );
}

/**
 * Judge #6 TUI Main Component
 * Zero-flicker rendering using Ink's declarative UI
 */

import { Box, Text } from "ink";
import Spinner from "ink-spinner";
import TextInput from "ink-text-input";
import type React from "react";
import { useState } from "react";
import { judge6 } from "../lib/judge6-client.js";
import type { ScanResponse } from "../types/index.js";
import { DecisionDisplay } from "./DecisionDisplay.js";

export const App: React.FC = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResponse | null>(null);
  const [history, setHistory] = useState<ScanResponse[]>([]);

  const handleSubmit = async (value: string) => {
    if (!value.trim()) return;

    setLoading(true);
    setQuery("");

    try {
      const response = await judge6.scan({
        purpose: value,
        atp519: true, // Enable binary compression
      });

      setResult(response);
      setHistory((prev) => [...prev, response]);
    } catch (error) {
      // Error handling would show error component
      console.error("Scan failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box flexDirection="column" paddingX={2} paddingY={1}>
      {/* Sticky Header */}
      <Box borderStyle="double" borderColor="cyan" paddingX={2}>
        <Text bold color="cyanBright">
          ⚖️ Judge #6 Governance Scanner v2.0
        </Text>
      </Box>

      <Box marginTop={1}>
        <Text dimColor>ATP 5-19 Compliance | Binary Decision Framework | p99≤90ms</Text>
      </Box>

      {/* Main Content Area */}
      <Box flexDirection="column" marginTop={1}>
        {loading && (
          <Box>
            <Text color="yellow">
              <Spinner type="dots" /> Analyzing decision...
            </Text>
          </Box>
        )}

        {result && !loading && (
          <DecisionDisplay
            decision={result.decision}
            latency_ms={result.latency_ms}
            cost_usd={result.cost_usd}
          />
        )}

        {!result && !loading && (
          <Box marginTop={2}>
            <Text dimColor>
              Enter a decision to validate against ATP 5-19 framework.{"\n"}
              Examples:{"\n"}• "Deploy new ML model to production"{"\n"}• "Grant admin access to
              contractor"{"\n"}• "Collect user behavioral data"
            </Text>
          </Box>
        )}
      </Box>

      {/* History Summary */}
      {history.length > 0 && (
        <Box marginTop={2} borderStyle="single" borderColor="gray" paddingX={1}>
          <Text dimColor>
            History: {history.length} decisions |{" "}
            {history.filter((h) => h.decision.brakes_pass).length} passed |{" "}
            {history.filter((h) => !h.decision.brakes_pass).length} failed
          </Text>
        </Box>
      )}

      {/* Anchored Input Prompt (Bottom) */}
      <Box marginTop={2} borderStyle="round" borderColor="green" paddingX={1}>
        <Box>
          <Text bold color="green">
            →{" "}
          </Text>
          <TextInput
            value={query}
            onChange={setQuery}
            onSubmit={handleSubmit}
            placeholder="Describe decision to validate..."
            showCursor
          />
        </Box>
      </Box>

      {/* Help Footer */}
      <Box marginTop={1}>
        <Text dimColor>
          Press Ctrl+C to exit | Binary compression: {result ? "✓" : "○"} | Flicker-free: ✓
        </Text>
      </Box>
    </Box>
  );
};

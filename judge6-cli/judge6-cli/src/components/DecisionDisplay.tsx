/**
 * Decision Display Component
 * Shows Judge #6 decision results with color coding
 */

import { Box, Text } from "ink";
import type React from "react";
import type { Judge6Decision } from "../types/index.js";
import { RiskMatrix } from "./RiskMatrix.js";

interface DecisionDisplayProps {
  decision: Judge6Decision;
  latency_ms: number;
  cost_usd: number;
}

export const DecisionDisplay: React.FC<DecisionDisplayProps> = ({
  decision,
  latency_ms,
  cost_usd,
}) => {
  return (
    <Box flexDirection="column" paddingX={1}>
      {/* Purpose */}
      <Box marginTop={1}>
        <Text bold color="cyan">
          Purpose:{" "}
        </Text>
        <Text>{decision.purpose}</Text>
      </Box>

      {/* Reasons */}
      <Box marginTop={1} flexDirection="column">
        <Text bold color="yellow">
          ⚠ Reasons:
        </Text>
        {decision.reasons.map((reason, idx) => (
          <Text key={idx} dimColor>
            {" "}
            • {reason}
          </Text>
        ))}
      </Box>

      {/* Brakes */}
      <Box marginTop={1}>
        <Text bold color={decision.brakes_pass ? "green" : "red"}>
          {decision.brakes_pass ? "✓" : "⊗"} Brakes:
        </Text>
        <Text color={decision.brakes_pass ? "green" : "red"}>
          {" "}
          {decision.brakes_pass ? "PASS" : "FAIL"}
        </Text>
      </Box>

      {/* Risk Matrix */}
      <RiskMatrix decision={decision} />

      {/* Binary Compression */}
      {decision.atp519_binary && (
        <Box marginTop={1} flexDirection="column">
          <Text bold color="magenta">
            Binary Decision (zstd compressed):
          </Text>
          <Text dimColor>
            {" "}
            {decision.atp519_binary} ({decision.atp519_bytes} bytes)
          </Text>
          <Text dimColor> Compression: 95% reduction from original</Text>
        </Box>
      )}

      {/* Metrics */}
      <Box marginTop={1} borderStyle="round" borderColor="gray" paddingX={1}>
        <Text dimColor>
          Latency: {latency_ms.toFixed(2)}ms | Cost: ${cost_usd.toFixed(4)} | Confidence:{" "}
          {(decision.confidence * 100).toFixed(1)}%
        </Text>
      </Box>
    </Box>
  );
};

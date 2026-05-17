/**
 * Risk Matrix Heatmap Component
 *
 * Displays ATP 5-19 risk matrix using ASCII art.
 */

import { Box, Text } from "ink";
import type React from "react";
import type { RiskLevel } from "../types.js";

interface RiskMatrixProps {
  riskLevel?: RiskLevel;
}

export const RiskMatrix: React.FC<RiskMatrixProps> = ({ riskLevel }) => {
  if (!riskLevel) {
    return null;
  }

  // Risk matrix (probability × severity)
  const matrix = [
    ["░", "░", "▒", "▓", "█"], // Severity 0 (Negligible)
    ["░", "▒", "▓", "█", "█"], // Severity 1 (Marginal)
    ["▒", "▓", "█", "█", "█"], // Severity 2 (Critical)
    ["▓", "█", "█", "█", "█"], // Severity 3 (Catastrophic)
  ];

  // Get color for rating
  const getRatingColor = (rating: string): string => {
    switch (rating) {
      case "RA-1":
        return "green";
      case "RA-2":
        return "yellow";
      case "RA-3":
        return "magenta";
      case "RA-4":
        return "red";
      default:
        return "white";
    }
  };

  const severityLabels = ["Negligible", "Marginal", "Critical", "Catastrophic"];
  const probabilityLabels = [
    "Extremely\nUnlikely",
    "Unlikely",
    "Moderately\nLikely",
    "Likely",
    "Very\nLikely",
  ];

  return (
    <Box flexDirection="column" marginTop={1}>
      <Text bold>Risk Matrix (ATP 5-19)</Text>
      <Box flexDirection="column" marginTop={1}>
        <Text dimColor> Probability →</Text>
        <Box>
          <Text dimColor>Severity ↓ </Text>
          <Text>┌───────────────────┐</Text>
        </Box>
        {matrix.map((row, severityIdx) => {
          const isCurrentRow = severityIdx === riskLevel.severity;
          return (
            <Box key={severityIdx}>
              <Text dimColor>{severityLabels[severityIdx].padEnd(12)}</Text>
              <Text>│ </Text>
              {row.map((cell, probIdx) => {
                const isCurrentCell = isCurrentRow && probIdx === riskLevel.probability;
                return (
                  <Text
                    key={probIdx}
                    color={isCurrentCell ? getRatingColor(riskLevel.rating) : undefined}
                    bold={isCurrentCell}
                  >
                    {isCurrentCell ? "█" : cell}{" "}
                  </Text>
                );
              })}
              <Text>│</Text>
            </Box>
          );
        })}
        <Text> └───────────────────┘</Text>
        <Box marginTop={1}>
          <Text bold>Result: </Text>
          <Text color={getRatingColor(riskLevel.rating)} bold>
            {riskLevel.rating}
          </Text>
          <Text dimColor>
            {" "}
            (P={riskLevel.probability}, S={riskLevel.severity})
          </Text>
        </Box>
      </Box>
    </Box>
  );
};

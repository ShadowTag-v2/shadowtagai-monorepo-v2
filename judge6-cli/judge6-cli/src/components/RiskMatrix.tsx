/**
 * ATP 5-19 Risk Matrix Visualization
 * Flicker-free rendering using Ink components
 */

import { Box, Text } from "ink";
import type React from "react";
import type { Judge6Decision } from "../types/index.js";

interface RiskMatrixProps {
  decision: Judge6Decision;
}

export const RiskMatrix: React.FC<RiskMatrixProps> = ({ decision }) => {
  const { probability, severity } = decision.risk;

  // Risk matrix cells (severity × probability)
  const matrix = [
    ["░", "░", "▒", "▓", "█"], // Severity 0
    ["░", "▒", "▓", "█", "█"], // Severity 1
    ["▒", "▓", "█", "█", "█"], // Severity 2
    ["▓", "█", "█", "█", "█"], // Severity 3
  ];

  const getColor = (row: number, col: number): string => {
    if (row === severity && col === probability) {
      return "red"; // Highlight current position
    }

    const score = col + row * 2;
    if (score >= 6) return "redBright";
    if (score >= 4) return "yellow";
    if (score >= 2) return "cyan";
    return "green";
  };

  return (
    <Box flexDirection="column" marginTop={1}>
      <Text bold color="cyan">
        Risk Matrix (ATP 5-19)
      </Text>
      <Box borderStyle="single" borderColor="cyan" paddingX={1}>
        <Box flexDirection="column">
          <Text dimColor> 0 1 2 3 4 ← Probability</Text>
          {matrix.map((row, rowIdx) => (
            <Box key={rowIdx}>
              <Text dimColor>{rowIdx} </Text>
              {row.map((cell, colIdx) => (
                <Text
                  key={colIdx}
                  color={getColor(rowIdx, colIdx)}
                  bold={rowIdx === severity && colIdx === probability}
                >
                  {rowIdx === severity && colIdx === probability ? "▓" : cell}
                </Text>
              ))}
            </Box>
          ))}
          <Text dimColor>↑ Severity</Text>
        </Box>
      </Box>
      <Box marginTop={1}>
        <Text>
          Result:{" "}
          <Text
            bold
            color={
              decision.risk_level === "CRITICAL"
                ? "red"
                : decision.risk_level === "HIGH"
                  ? "yellow"
                  : decision.risk_level === "MEDIUM"
                    ? "cyan"
                    : "green"
            }
          >
            {decision.risk_level}
          </Text>
        </Text>
      </Box>
    </Box>
  );
};

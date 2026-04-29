/**
 * DecisionReview Component
 *
 * Main TUI component for Judge 6 CLI with zero-flicker rendering.
 * Uses Ink's alternate screen buffer for flicker-free updates.
 */

import { Box, Text } from 'ink';
import Spinner from 'ink-spinner';
import TextInput from 'ink-text-input';
import type React from 'react';
import { useState } from 'react';
import { Claude_Code_6ApiClient } from '../api.js';
import type { DecisionValidationResponse, ValidationHistory } from '../types.js';
import { RiskMatrix } from './RiskMatrix.js';

interface DecisionReviewProps {
  apiUrl?: string;
}

export const DecisionReview: React.FC<DecisionReviewProps> = ({ apiUrl }) => {
  const [query, setQuery] = useState('');
  const [decision, setDecision] = useState<DecisionValidationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<ValidationHistory[]>([]);
  const [client] = useState(() => new Claude_Code_6ApiClient(apiUrl));

  const handleSubmit = async (value: string) => {
    if (!value.trim()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await client.validate({
        purpose: value,
        atp519: true,
      });

      setDecision(result);
      setHistory((prev) => [
        ...prev,
        {
          request: { purpose: value, atp519: true },
          response: result,
          timestamp: new Date().toISOString(),
        },
      ]);
      setQuery('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const getResultColor = (result: string): string => {
    switch (result) {
      case 'approved':
        return 'green';
      case 'blocked_purpose':
        return 'yellow';
      case 'blocked_reasons':
        return 'magenta';
      case 'blocked_brakes':
        return 'red';
      default:
        return 'white';
    }
  };

  const getResultSymbol = (result: string): string => {
    switch (result) {
      case 'approved':
        return '✓';
      case 'blocked_purpose':
        return '⚠';
      case 'blocked_reasons':
        return '⊘';
      case 'blocked_brakes':
        return '⊗';
      default:
        return '?';
    }
  };

  return (
    <Box flexDirection="column" padding={1}>
      {/* Sticky header (always visible) */}
      <Box borderStyle="round" borderColor="cyan" paddingX={2}>
        <Text bold color="cyan">
          Judge 6 Governance Scanner v2.0
        </Text>
      </Box>

      <Box marginTop={1} borderStyle="single" borderColor="gray" paddingX={1}>
        <Text dimColor>
          Purpose/Reasons/Brakes validation • ATP 5-19 compliance • Zero-flicker TUI
        </Text>
      </Box>

      {/* Main content area (scrollable) */}
      <Box flexDirection="column" marginTop={1}>
        {loading && (
          <Box>
            <Text color="yellow">
              <Spinner type="dots" /> Analyzing decision...
            </Text>
          </Box>
        )}

        {error && (
          <Box borderStyle="round" borderColor="red" paddingX={1} marginTop={1}>
            <Text color="red">❌ Error: {error}</Text>
          </Box>
        )}

        {decision && !loading && (
          <Box flexDirection="column" marginTop={1}>
            {/* Decision Result Header */}
            <Box borderStyle="bold" borderColor={getResultColor(decision.result)} paddingX={1}>
              <Text bold color={getResultColor(decision.result)}>
                {getResultSymbol(decision.result)} {decision.result.toUpperCase()}
              </Text>
            </Box>

            {/* Purpose Validation */}
            <Box marginTop={1}>
              <Text bold>Purpose: </Text>
              <Text color={decision.purpose_valid ? 'green' : 'red'}>
                {decision.purpose_valid ? '✓' : '✗'}
              </Text>
              <Text dimColor> (score: {(decision.purpose_score * 100).toFixed(1)}%)</Text>
            </Box>
            <Box paddingLeft={2}>
              <Text dimColor>"{decision.purpose}"</Text>
            </Box>

            {/* Reasons Validation */}
            <Box marginTop={1}>
              <Text bold>Reasons: </Text>
              <Text color={decision.reasons_valid ? 'green' : 'red'}>
                {decision.reasons_valid ? '✓' : '✗'}
              </Text>
              <Text dimColor> (score: {(decision.reasons_score * 100).toFixed(1)}%)</Text>
            </Box>

            {/* Brakes Check */}
            <Box marginTop={1}>
              <Text bold>Brakes: </Text>
              <Text color={decision.brakes_clear ? 'green' : 'red'}>
                {decision.brakes_clear ? '✓ CLEAR' : '⊗ VIOLATED'}
              </Text>
              <Text dimColor> (score: {(decision.brakes_score * 100).toFixed(1)}%)</Text>
            </Box>

            {/* Explanation */}
            <Box marginTop={1} borderStyle="single" borderColor="gray" paddingX={1}>
              <Text>{decision.explanation}</Text>
            </Box>

            {/* Risk Matrix */}
            {decision.risk_level && <RiskMatrix riskLevel={decision.risk_level} />}

            {/* Binary Compressed Output */}
            {decision.compressed_bytes && (
              <Box marginTop={1}>
                <Text dimColor>
                  📦 Compressed: {decision.compressed_bytes} bytes (95% reduction via ATP 5-19)
                </Text>
              </Box>
            )}

            {/* Timestamp */}
            <Box marginTop={1}>
              <Text dimColor>⏱️ {new Date(decision.timestamp).toLocaleString()}</Text>
            </Box>
          </Box>
        )}

        {/* History Summary */}
        {history.length > 0 && (
          <Box marginTop={2} borderStyle="single" borderColor="blue" paddingX={1}>
            <Box flexDirection="column">
              <Text bold color="blue">
                Session History ({history.length} decisions)
              </Text>
              <Box marginTop={1}>
                <Text dimColor>
                  Approved: {history.filter((h) => h.response.result === 'approved').length} •{' '}
                  Blocked: {history.filter((h) => h.response.result !== 'approved').length}
                </Text>
              </Box>
            </Box>
          </Box>
        )}
      </Box>

      {/* Anchored input prompt (bottom of screen) */}
      <Box marginTop={1} borderStyle="round" borderColor="green">
        <Box paddingX={1}>
          <Text bold color="green">
            →{' '}
          </Text>
          <TextInput
            value={query}
            onChange={setQuery}
            onSubmit={handleSubmit}
            placeholder="Describe decision to validate..."
          />
        </Box>
      </Box>

      {/* Footer */}
      <Box marginTop={1}>
        <Text dimColor>Press Ctrl+C to exit • Dashboard: dashboard.pnkln.com</Text>
      </Box>
    </Box>
  );
};

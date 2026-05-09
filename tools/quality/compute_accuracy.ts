/**
 * V23 Quality Accuracy Computer — Task 1
 * Parses .beads/repo_doctor_latest.json and computes
 * semantic match accuracy from the speculation telemetry.
 */

import { readFileSync, existsSync } from "fs";
import { join } from "path";

interface RepoDoctor {
  total_evals?: number;
  semantic_matches?: number;
  checks?: Array<{
    name: string;
    passed: boolean;
    details?: string;
  }>;
  timestamp?: string;
}

interface TelemetryEntry {
  intent_predicted: string;
  intent_actual: string;
  confidence: number;
  latency_ms: number;
  timestamp: number;
}

export function computeQualityAccuracy(
  workspaceRoot: string = process.cwd(),
): {
  accuracy: number;
  total: number;
  matches: number;
  source: "beads" | "telemetry" | "empty";
} {
  // Try .beads/repo_doctor_latest.json first
  const beadPath = join(workspaceRoot, ".beads", "repo_doctor_latest.json");
  if (existsSync(beadPath)) {
    try {
      const data: RepoDoctor = JSON.parse(readFileSync(beadPath, "utf-8"));
      if (data.total_evals && data.semantic_matches) {
        const accuracy = data.semantic_matches / data.total_evals;
        return {
          accuracy,
          total: data.total_evals,
          matches: data.semantic_matches,
          source: "beads",
        };
      }
    } catch {
      // Fall through to telemetry
    }
  }

  // Try .beads/speculation_telemetry.jsonl
  const telemetryPath = join(workspaceRoot, ".beads", "speculation_telemetry.jsonl");
  if (existsSync(telemetryPath)) {
    try {
      const lines = readFileSync(telemetryPath, "utf-8")
        .split("\n")
        .filter((l) => l.trim());
      const entries: TelemetryEntry[] = lines.map((l) => JSON.parse(l));
      const matches = entries.filter(
        (e) => e.intent_predicted === e.intent_actual,
      ).length;
      return {
        accuracy: entries.length > 0 ? matches / entries.length : 0,
        total: entries.length,
        matches,
        source: "telemetry",
      };
    } catch {
      // Fall through
    }
  }

  return { accuracy: 0, total: 0, matches: 0, source: "empty" };
}

// CLI entry point
if (
  typeof process !== "undefined" &&
  process.argv[1]?.endsWith("compute_accuracy.ts")
) {
  const result = computeQualityAccuracy();
  console.log(
    `⚡ [KAIROS] Quality Accuracy: ${(result.accuracy * 100).toFixed(2)}% ` +
      `(${result.matches}/${result.total} from ${result.source})`,
  );
}

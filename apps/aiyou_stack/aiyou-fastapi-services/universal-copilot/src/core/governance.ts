/**
 * Judge 6 Governance Integration Adapter
 * Provides safe interface to Python-based Judge 6 system
 */

import { spawn } from "node:child_process";
import * as path from "node:path";
import type { GovernanceEngine } from "./router.js";

/**
 * Judge 6 governance decision
 */
export interface Judge6Decision {
  approved: boolean;
  risk_level: string;
  reasoning: string;
  violated_axioms: Array<{
    axiom_id: string;
    name: string;
    rule: string;
  }>;
  provenance_stamp: {
    timestamp: string;
    signature: string;
  } | null;
  metadata: Record<string, unknown>;
}

/**
 * Python Judge 6 adapter
 * Calls Python Judge 6 implementation via subprocess
 */
export class Judge6Adapter implements GovernanceEngine {
  private corInstanceId: string;
  private pythonPath: string;
  private judge6Path: string;

  constructor(corInstanceId: string = "copilot-001", pythonPath: string = "python3") {
    this.corInstanceId = corInstanceId;
    this.pythonPath = pythonPath;

    // Path to judge6 Python package
    this.judge6Path = path.join(process.cwd(), "..", "judge6");
  }

  async evaluateRequest(input: string, purpose?: string): Promise<Judge6Decision> {
    return new Promise((resolve, reject) => {
      // Build Python script to evaluate request
      const script = this.buildEvaluationScript(input, purpose);

      // Spawn Python process
      const proc = spawn(this.pythonPath, ["-c", script], {
        cwd: process.cwd(),
        env: {
          ...process.env,
          PYTHONPATH: path.dirname(this.judge6Path),
        },
      });

      let stdout = "";
      let stderr = "";

      proc.stdout.on("data", (data) => {
        stdout += data.toString();
      });

      proc.stderr.on("data", (data) => {
        stderr += data.toString();
      });

      proc.on("close", (code) => {
        if (code !== 0) {
          reject(new Error(`Judge 6 evaluation failed: ${stderr || "Unknown error"}`));
          return;
        }

        try {
          const decision = JSON.parse(stdout) as Judge6Decision;
          resolve(decision);
        } catch (error) {
          reject(new Error(`Failed to parse Judge 6 response: ${error}`));
        }
      });

      proc.on("error", (error) => {
        reject(new Error(`Failed to spawn Judge 6 process: ${error.message}`));
      });

      // Timeout after 5 seconds
      setTimeout(() => {
        proc.kill();
        reject(new Error("Judge 6 evaluation timeout"));
      }, 5000);
    });
  }

  private buildEvaluationScript(input: string, purpose?: string): string {
    // Escape strings for Python
    const escapedInput = this.escapePython(input);
    const escapedPurpose = purpose ? this.escapePython(purpose) : "None";

    return `
import sys
import json
sys.path.insert(0, "${this.escapePython(path.dirname(this.judge6Path))}")

from judge6 import JudgmentRule

judge = JudgmentRule(cor_instance_id="${this.escapePython(this.corInstanceId)}")

user_input = """${escapedInput}"""
declared_purpose = ${escapedPurpose === "None" ? "None" : `"""${escapedPurpose}"""`}

decision = judge.evaluate_request(user_input, declared_purpose)

result = {
    "approved": decision.approved,
    "risk_level": decision.risk_level.value,
    "reasoning": decision.reasoning,
    "violated_axioms": [
        {
            "axiom_id": ax.axiom_id,
            "name": ax.name,
            "rule": ax.rule
        }
        for ax in decision.violated_axioms
    ],
    "provenance_stamp": {
        "timestamp": decision.provenance_stamp.timestamp,
        "signature": decision.provenance_stamp.signature
    } if decision.provenance_stamp else None,
    "metadata": decision.metadata
}

print(json.dumps(result))
`;
  }

  private escapePython(str: string): string {
    return str
      .replace(/\\/g, "\\\\")
      .replace(/"/g, '\\"')
      .replace(/\n/g, "\\n")
      .replace(/\r/g, "\\r")
      .replace(/\t/g, "\\t");
  }
}

/**
 * Mock governance for testing without Python dependency
 */
export class MockGovernance implements GovernanceEngine {
  async evaluateRequest(input: string, purpose?: string): Promise<Judge6Decision> {
    // Simple mock: reject if input contains "malware" or "exploit"
    const dangerous = /\b(malware|exploit|hack|bypass|jailbreak)\b/i.test(input);

    return {
      approved: !dangerous,
      risk_level: dangerous ? "RA_3" : "RA_1",
      reasoning: dangerous
        ? "Mock governance: Detected potentially harmful intent"
        : "Mock governance: Request approved",
      violated_axioms: dangerous
        ? [
            {
              axiom_id: "A2",
              name: "HARM_PROHIBITION",
              rule: "No output may facilitate harm",
            },
          ]
        : [],
      provenance_stamp: null,
      metadata: {
        mock: true,
        input_length: input.length,
      },
    };
  }
}

/**
 * Create governance engine based on environment
 */
export function createGovernance(
  useMock: boolean = process.env.USE_MOCK_GOVERNANCE === "1",
): GovernanceEngine {
  if (useMock) {
    return new MockGovernance();
  }
  return new Judge6Adapter();
}

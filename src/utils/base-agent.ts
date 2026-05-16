/**
 * Base Agent Class
 * Provides common functionality for all agents
 */

import type {
  Agent,
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from "../types/agent.types";

export abstract class BaseAgent implements Agent {
  abstract metadata: AgentMetadata;
  abstract prompt: AgentPromptTemplate;
  abstract tools: AgentTools;
  abstract workflow: AgentWorkflow;

  async execute(context: AgentExecutionContext): Promise<AgentResult> {
    const startTime = Date.now();
    const result: AgentResult = {
      success: false,
      output: "",
      artifacts: {
        filesCreated: [],
        filesModified: [],
        filesDeleted: [],
      },
      metrics: {
        executionTimeMs: 0,
        stepsCompleted: 0,
      },
      errors: [],
      recommendations: [],
    };

    try {
      // Validate context
      this.validateContext(context);

      // Execute workflow steps
      for (let i = 0; i < this.workflow.steps.length; i++) {
        const step = this.workflow.steps[i];

        try {
          await this.executeStep(step, context, result);
          const metrics = result.metrics ?? { executionTimeMs: 0, stepsCompleted: 0 };
          metrics.stepsCompleted++;
          result.metrics = metrics;
        } catch (error) {
          result.errors?.push({
            code: `STEP_${i}_FAILED`,
            message: `Failed to execute step: ${step.name}`,
            details: error,
          });

          if (!this.canContinueOnError(step, error)) {
            throw error;
          }
        }
      }

      result.success = result.errors?.length === 0;
      result.output = this.generateOutput(result);
    } catch (error) {
      result.success = false;
      result.errors?.push({
        code: "EXECUTION_FAILED",
        message: error instanceof Error ? error.message : "Unknown error",
        details: error,
      });
    } finally {
      const finalMetrics = result.metrics ?? { executionTimeMs: 0, stepsCompleted: 0 };
      finalMetrics.executionTimeMs = Date.now() - startTime;
      result.metrics = finalMetrics;
    }

    return result;
  }

  protected abstract executeStep(
    step: AgentWorkflow["steps"][0],
    context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void>;

  protected validateContext(context: AgentExecutionContext): void {
    if (!context.projectPath) {
      throw new Error("Project path is required");
    }
    if (!context.userQuery) {
      throw new Error("User query is required");
    }
  }

  protected canContinueOnError(_step: AgentWorkflow["steps"][0], _error: unknown): boolean {
    // Override in subclasses to define error handling strategy
    return false;
  }

  protected generateOutput(result: AgentResult): string {
    let output = `Agent: ${this.metadata.name}\n\n`;

    if (result.success) {
      output += "✅ Execution completed successfully\n\n";
    } else {
      output += "❌ Execution completed with errors\n\n";
    }

    output += `Steps completed: ${result.metrics?.stepsCompleted}/${this.workflow.steps.length}\n`;
    output += `Execution time: ${result.metrics?.executionTimeMs}ms\n\n`;

    if (result.artifacts?.filesCreated?.length) {
      output += `Files created: ${result.artifacts.filesCreated.length}\n`;
    }
    if (result.artifacts?.filesModified?.length) {
      output += `Files modified: ${result.artifacts.filesModified.length}\n`;
    }
    if (result.artifacts?.filesDeleted?.length) {
      output += `Files deleted: ${result.artifacts.filesDeleted.length}\n`;
    }

    if (result.errors?.length) {
      output += "\n⚠️  Errors:\n";
      for (const [index, error] of result.errors.entries()) {
        output += `${index + 1}. [${error.code}] ${error.message}\n`;
      }
    }

    if (result.recommendations?.length) {
      output += "\n💡 Recommendations:\n";
      for (const [index, rec] of result.recommendations.entries()) {
        output += `${index + 1}. ${rec}\n`;
      }
    }

    return output;
  }
}

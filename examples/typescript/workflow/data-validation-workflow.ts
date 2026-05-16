/**
 * Workflow Pattern Reference Implementation
 *
 * This example demonstrates a production-ready workflow agent for data validation.
 * Key features:
 * - Deterministic execution path
 * - Comprehensive error handling
 * - Full observability
 * - Self-validation
 */

import { query } from "@anthropic-ai/claude-agent-sdk";

// ==================== Types ====================

interface WorkflowStep {
  name: string;
  execute: (context: WorkflowContext) => Promise<any>;
  validate: (result: any) => boolean;
  onError?: (error: Error, context: WorkflowContext) => Promise<any>;
}

interface WorkflowContext {
  input: any;
  results: Record<string, any>;
  metadata: {
    startTime: number;
    stepResults: StepResult[];
  };
}

interface StepResult {
  step: string;
  success: boolean;
  duration: number;
  error?: string;
}

interface ValidationReport {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  summary: string;
}

interface ValidationError {
  field: string;
  message: string;
  severity: "critical" | "high" | "medium";
}

interface ValidationWarning {
  field: string;
  message: string;
}

// ==================== System Prompt ====================

const WORKFLOW_SYSTEM_PROMPT = `
<agent_configuration>
  <metadata>
    <agent_name>Data Validation Workflow</agent_name>
    <pattern>workflow</pattern>
    <version>1.0.0</version>
  </metadata>

  <role>
You are a data validation agent that processes user submissions through
a defined validation pipeline. You follow a strict, deterministic workflow
to ensure data quality and compliance.
  </role>

  <workflow_definition>
Step 1: CLASSIFY INPUT TYPE
- Identify data format (CSV, JSON, XML, etc.)
- Determine validation rules to apply
- Select appropriate schema

Step 2: SCHEMA VALIDATION
- Validate against predefined schema
- Check required fields
- Verify data types

Step 3: BUSINESS RULE VALIDATION
- Apply domain-specific rules
- Check constraints and relationships
- Validate calculations

Step 4: QUALITY CHECKS
- Check for duplicates
- Validate data ranges
- Verify referential integrity

Step 5: GENERATE REPORT
- Compile validation results
- List all errors and warnings
- Provide remediation guidance
  </workflow_definition>

  <quality_standards>
Every validation must:
- Process all records (no partial failures)
- Generate comprehensive error reports
- Complete within 30 seconds for <10MB files
- Achieve 100% rule coverage
  </quality_standards>

  <constraints>
Must NOT:
- Skip validation steps
- Proceed with invalid data
- Make assumptions about missing fields

Must:
- Log every step and decision
- Provide clear, actionable error messages
- Maintain data integrity
  </constraints>
</agent_configuration>
`;

// ==================== Workflow Steps ====================

const classifyInputStep: WorkflowStep = {
  name: "classify_input",
  execute: async (context: WorkflowContext) => {
    console.log("[Step 1] Classifying input type...");

    const result = await query({
      prompt: `
Analyze this data and determine:
1. Data format (JSON, CSV, XML, etc.)
2. Schema structure
3. Appropriate validation rules

Data:
${JSON.stringify(context.input, null, 2)}

Return a JSON object with: { format: string, schema: object, rules: string[] }
      `,
      options: {
        systemPrompt: WORKFLOW_SYSTEM_PROMPT,
        maxTokens: 2000,
        model: "claude-sonnet-4.5-20250514",
      },
    });

    return JSON.parse(result);
  },
  validate: (result) => {
    return result && result.format && result.schema && Array.isArray(result.rules);
  },
};

const schemaValidationStep: WorkflowStep = {
  name: "schema_validation",
  execute: async (context: WorkflowContext) => {
    console.log("[Step 2] Validating against schema...");

    const schema = context.results.classify_input.schema;

    const result = await query({
      prompt: `
Validate this data against the schema:

Data:
${JSON.stringify(context.input, null, 2)}

Schema:
${JSON.stringify(schema, null, 2)}

Check:
1. All required fields present
2. Data types match schema
3. Value constraints satisfied

Return JSON: { valid: boolean, errors: Array<{field, message, severity}> }
      `,
      options: {
        systemPrompt: WORKFLOW_SYSTEM_PROMPT,
        maxTokens: 3000,
        model: "claude-sonnet-4.5-20250514",
      },
    });

    return JSON.parse(result);
  },
  validate: (result) => {
    return result && typeof result.valid === "boolean" && Array.isArray(result.errors);
  },
};

const businessRuleValidationStep: WorkflowStep = {
  name: "business_rule_validation",
  execute: async (context: WorkflowContext) => {
    console.log("[Step 3] Applying business rules...");

    const rules = context.results.classify_input.rules;

    const result = await query({
      prompt: `
Apply these business rules to the data:

Data:
${JSON.stringify(context.input, null, 2)}

Rules:
${rules.join("\n")}

Validate each rule and return:
{ valid: boolean, violations: Array<{rule, field, message}> }
      `,
      options: {
        systemPrompt: WORKFLOW_SYSTEM_PROMPT,
        maxTokens: 3000,
        model: "claude-sonnet-4.5-20250514",
      },
    });

    return JSON.parse(result);
  },
  validate: (result) => {
    return result && typeof result.valid === "boolean" && Array.isArray(result.violations);
  },
};

const qualityChecksStep: WorkflowStep = {
  name: "quality_checks",
  execute: async (context: WorkflowContext) => {
    console.log("[Step 4] Running quality checks...");

    const result = await query({
      prompt: `
Perform quality checks on this data:

${JSON.stringify(context.input, null, 2)}

Check for:
1. Duplicate records
2. Data range validation
3. Referential integrity
4. Data consistency

Return: { warnings: Array<{field, message, type}> }
      `,
      options: {
        systemPrompt: WORKFLOW_SYSTEM_PROMPT,
        maxTokens: 2000,
        model: "claude-sonnet-4.5-20250514",
      },
    });

    return JSON.parse(result);
  },
  validate: (result) => {
    return result && Array.isArray(result.warnings);
  },
};

const generateReportStep: WorkflowStep = {
  name: "generate_report",
  execute: async (context: WorkflowContext) => {
    console.log("[Step 5] Generating validation report...");

    const schemaErrors = context.results.schema_validation.errors;
    const businessViolations = context.results.business_rule_validation.violations;
    const qualityWarnings = context.results.quality_checks.warnings;

    const result = await query({
      prompt: `
Generate a comprehensive validation report.

Schema Errors:
${JSON.stringify(schemaErrors, null, 2)}

Business Rule Violations:
${JSON.stringify(businessViolations, null, 2)}

Quality Warnings:
${JSON.stringify(qualityWarnings, null, 2)}

Create a report with:
1. Executive summary
2. Critical issues (must fix)
3. Warnings (should fix)
4. Recommendations
5. Overall validation status

Return JSON: {
  valid: boolean,
  errors: Array<{field, message, severity}>,
  warnings: Array<{field, message}>,
  summary: string
}
      `,
      options: {
        systemPrompt: WORKFLOW_SYSTEM_PROMPT,
        maxTokens: 4000,
        model: "claude-sonnet-4.5-20250514",
      },
    });

    return JSON.parse(result);
  },
  validate: (result) => {
    return result && typeof result.valid === "boolean" && result.summary;
  },
};

// ==================== Workflow Engine ====================

class WorkflowEngine {
  private steps: WorkflowStep[];

  constructor(steps: WorkflowStep[]) {
    this.steps = steps;
  }

  async execute(input: any): Promise<ValidationReport> {
    const context: WorkflowContext = {
      input,
      results: {},
      metadata: {
        startTime: Date.now(),
        stepResults: [],
      },
    };

    for (const step of this.steps) {
      const stepStartTime = Date.now();

      try {
        console.log(`\n=== Executing: ${step.name} ===`);

        const result = await step.execute(context);

        if (!step.validate(result)) {
          throw new Error(`Validation failed for step: ${step.name}`);
        }

        context.results[step.name] = result;

        const duration = Date.now() - stepStartTime;
        context.metadata.stepResults.push({
          step: step.name,
          success: true,
          duration,
        });

        console.log(`✓ ${step.name} completed in ${duration}ms`);
      } catch (error) {
        const duration = Date.now() - stepStartTime;

        console.error(`✗ ${step.name} failed:`, error.message);

        context.metadata.stepResults.push({
          step: step.name,
          success: false,
          duration,
          error: error.message,
        });

        if (step.onError) {
          console.log(`Attempting error recovery for ${step.name}...`);
          await step.onError(error, context);
        } else {
          throw error;
        }
      }
    }

    const totalDuration = Date.now() - context.metadata.startTime;
    console.log(`\n=== Workflow completed in ${totalDuration}ms ===`);

    return context.results.generate_report as ValidationReport;
  }
}

// ==================== Main ====================

async function main() {
  // Example input data with issues
  const testData = {
    users: [
      {
        name: "John Doe",
        email: "john@example.com",
        age: 30,
        role: "admin",
      },
      {
        name: "Jane Smith",
        email: "invalid-email", // Invalid email
        age: -5, // Invalid age
        role: "user",
      },
      {
        name: "John Doe", // Duplicate
        email: "john@example.com",
        age: 30,
        role: "admin",
      },
    ],
  };

  // Create and execute workflow
  const workflow = new WorkflowEngine([
    classifyInputStep,
    schemaValidationStep,
    businessRuleValidationStep,
    qualityChecksStep,
    generateReportStep,
  ]);

  try {
    const report = await workflow.execute(testData);

    console.log("\n=== VALIDATION REPORT ===");
    console.log(JSON.stringify(report, null, 2));

    if (report.valid) {
      console.log("\n✓ Data is valid and ready for processing");
    } else {
      console.log("\n✗ Data validation failed");
      console.log(`Errors: ${report.errors.length}`);
      console.log(`Warnings: ${report.warnings.length}`);
    }
  } catch (error) {
    console.error("\n✗ Workflow execution failed:", error.message);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

// Export for use as module
export { type ValidationReport, type WorkflowContext, WorkflowEngine, type WorkflowStep };

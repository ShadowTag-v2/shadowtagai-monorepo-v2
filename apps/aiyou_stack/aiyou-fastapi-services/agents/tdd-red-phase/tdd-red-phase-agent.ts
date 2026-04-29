/**
 * TDD Red-Phase Agent with Embedded Guard Validation
 *
 * Architecture: Single agent, two internal phases
 * - Phase 1: Test Generation
 * - Phase 2: Self-Verification (embedded guard)
 *
 * Eliminates 3-agent circular dependency coordination overhead
 *
 * @doctrine Pnkln Core: Insanely great through elegant simplicity
 * @version 1.0.0
 */

import * as fs from 'fs';
import * as path from 'path';

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

interface ComplianceRule {
  id: string;
  name: string;
  description: string;
  weight: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
  enforcement: 'mandatory' | 'recommended';
  [key: string]: unknown;
}

interface ComplianceConfig {
  version: string;
  compliance_threshold: number;
  max_iterations: number;
  timeout_seconds: number;
  fail_fast_violations: number;
  Claude_Code_6_integration: {
    coverage_target: number;
    latency_p99_ms: number;
  };
  rules: ComplianceRule[];
  escalation: {
    path: string;
    trigger_conditions: string[];
    notification_channels: string[];
  };
  audit: {
    enabled: boolean;
    output_dir: string;
    format: string;
    filename_pattern: string;
    retention_days: number;
    include_fields: string[];
  };
}

interface Violation {
  rule_id: string;
  rule_name: string;
  severity: string;
  description: string;
  location?: string;
  suggestion?: string;
}

interface ComplianceReport {
  timestamp: string;
  iteration: number;
  violations_found: Violation[];
  corrections_applied: string[];
  compliance_score: number;
  passed: boolean;
  execution_time_ms: number;
  escalation_triggered: boolean;
  escalation_reason?: string;
}

interface TestSuite {
  module: string;
  tests: Test[];
  metadata: {
    total_tests: number;
    integration_tests: number;
    unit_tests: number;
    integration_ratio: number;
  };
}

interface Test {
  name: string;
  type: 'integration' | 'unit';
  code: string;
  assertions: number;
  purpose: string;
  edge_cases_covered: string[];
}

interface AgentResult {
  success: boolean;
  test_suite: TestSuite | null;
  compliance_report: ComplianceReport;
  audit_file_path?: string;
}

// ============================================================================
// TDD RED-PHASE AGENT (with embedded guard)
// ============================================================================

export class TDDRedPhaseAgent {
  private config: ComplianceConfig;
  private startTime: number = 0;
  private iteration: number = 0;

  constructor(configPath: string = '../../src/config/tdd-compliance-rules.json') {
    const resolvedPath = path.resolve(__dirname, configPath);
    const configData = fs.readFileSync(resolvedPath, 'utf-8');
    this.config = JSON.parse(configData);
  }

  /**
   * Main execution: Generate tests + embedded self-verification
   *
   * @param requirements - Requirements or module to test
   * @returns AgentResult with tests and compliance report
   */
  async execute(requirements: string): Promise<AgentResult> {
    this.startTime = Date.now();
    this.iteration = 0;

    try {
      // Phase 1: Generate initial test suite
      let testSuite = await this.generateTests(requirements);

      // Phase 2: Self-verification loop (embedded guard)
      let complianceReport = await this.selfVerify(testSuite);

      // Iteration loop with kill switch
      while (!complianceReport.passed && this.iteration < this.config.max_iterations) {
        // Check timeout
        if (this.isTimedOut()) {
          complianceReport.escalation_triggered = true;
          complianceReport.escalation_reason = 'timeout_reached';
          break;
        }

        this.iteration++;

        // Self-correct based on violations
        testSuite = await this.selfCorrect(testSuite, complianceReport.violations_found);

        // Re-verify
        complianceReport = await this.selfVerify(testSuite);
      }

      // Escalation if max iterations exceeded
      if (this.iteration >= this.config.max_iterations && !complianceReport.passed) {
        complianceReport.escalation_triggered = true;
        complianceReport.escalation_reason = 'iterations_exceeded';
      }

      // Generate audit trail
      const auditPath = this.config.audit.enabled
        ? await this.generateAuditTrail(complianceReport)
        : undefined;

      return {
        success: complianceReport.passed,
        test_suite: testSuite,
        compliance_report: complianceReport,
        audit_file_path: auditPath,
      };
    } catch (error) {
      const errorReport: ComplianceReport = {
        timestamp: new Date().toISOString(),
        iteration: this.iteration,
        violations_found: [
          {
            rule_id: 'SYSTEM',
            rule_name: 'execution_error',
            severity: 'critical',
            description: `Agent execution failed: ${(error as Error).message}`,
          },
        ],
        corrections_applied: [],
        compliance_score: 0,
        passed: false,
        execution_time_ms: Date.now() - this.startTime,
        escalation_triggered: true,
        escalation_reason: 'execution_error',
      };

      return {
        success: false,
        test_suite: null,
        compliance_report: errorReport,
      };
    }
  }

  // ==========================================================================
  // PHASE 1: TEST GENERATION
  // ==========================================================================

  /**
   * Generate comprehensive test suite from requirements
   * Integration-first: 80% integration, 20% unit (per 80/20 doctrine)
   */
  private async generateTests(requirements: string): Promise<TestSuite> {
    // Parse requirements and identify testable components
    const module = this.extractModuleName(requirements);

    // Generate integration tests (80%)
    const integrationTests = await this.generateIntegrationTests(requirements);

    // Generate unit tests (20%)
    const unitTests = await this.generateUnitTests(requirements);

    const tests = [...integrationTests, ...unitTests];
    const integrationCount = integrationTests.length;
    const totalCount = tests.length;

    return {
      module,
      tests,
      metadata: {
        total_tests: totalCount,
        integration_tests: integrationCount,
        unit_tests: unitTests.length,
        integration_ratio: totalCount > 0 ? integrationCount / totalCount : 0,
      },
    };
  }

  private extractModuleName(requirements: string): string {
    // Extract module name from requirements
    const match = requirements.match(/module[:\s]+([a-zA-Z0-9_-]+)/i);
    return match ? match[1] : 'unnamed_module';
  }

  private async generateIntegrationTests(requirements: string): Promise<Test[]> {
    // Simplified generation - in production, use LLM for smart generation
    // Focus on end-to-end workflows and API contracts

    const integrationTests: Test[] = [
      {
        name: 'test_should_complete_full_workflow_when_valid_input',
        type: 'integration',
        code: this.generateIntegrationTestCode('full_workflow', requirements),
        assertions: 3,
        purpose: 'Verify complete workflow from input to output',
        edge_cases_covered: ['happy_path', 'typical_scenario'],
      },
      {
        name: 'test_should_handle_external_service_failure_when_dependency_unavailable',
        type: 'integration',
        code: this.generateIntegrationTestCode('service_failure', requirements),
        assertions: 2,
        purpose: 'Verify graceful degradation on external failures',
        edge_cases_covered: ['service_down', 'timeout'],
      },
      {
        name: 'test_should_maintain_data_integrity_when_concurrent_operations',
        type: 'integration',
        code: this.generateIntegrationTestCode('concurrency', requirements),
        assertions: 4,
        purpose: 'Verify thread safety and data consistency',
        edge_cases_covered: ['race_condition', 'concurrent_writes'],
      },
      {
        name: 'test_should_validate_api_contract_when_integration_points_called',
        type: 'integration',
        code: this.generateIntegrationTestCode('api_contract', requirements),
        assertions: 5,
        purpose: 'Verify API contract compliance',
        edge_cases_covered: ['schema_validation', 'response_format'],
      },
    ];

    return integrationTests;
  }

  private async generateUnitTests(requirements: string): Promise<Test[]> {
    // Generate focused unit tests for critical logic

    const unitTests: Test[] = [
      {
        name: 'test_should_return_null_when_input_is_null',
        type: 'unit',
        code: this.generateUnitTestCode('null_input', requirements),
        assertions: 1,
        purpose: 'Verify null handling',
        edge_cases_covered: ['null'],
      },
      {
        name: 'test_should_return_empty_when_input_is_empty',
        type: 'unit',
        code: this.generateUnitTestCode('empty_input', requirements),
        assertions: 1,
        purpose: 'Verify empty input handling',
        edge_cases_covered: ['empty'],
      },
    ];

    return unitTests;
  }

  private generateIntegrationTestCode(scenario: string, requirements: string): string {
    // Simplified code generation - in production, use LLM
    return `
def test_${scenario}(self):
    """Integration test for ${scenario}"""
    # Setup
    service = ServiceUnderTest()

    # Execute
    result = service.execute()

    # Assert
    assert result is not None
    assert result.success is True

    # Teardown
    service.cleanup()
`;
  }

  private generateUnitTestCode(scenario: string, requirements: string): string {
    return `
def test_${scenario}(self):
    """Unit test for ${scenario}"""
    # Arrange
    input_data = None  # or appropriate test data

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_value
`;
  }

  // ==========================================================================
  // PHASE 2: SELF-VERIFICATION (Embedded Guard)
  // ==========================================================================

  /**
   * Embedded guard validation - replaces separate tdd-guard agent
   * Single responsibility: Inspect and validate against compliance rules
   */
  private async selfVerify(testSuite: TestSuite): Promise<ComplianceReport> {
    const violations: Violation[] = [];
    let totalWeight = 0;
    let achievedWeight = 0;

    // Check against each rule
    for (const rule of this.config.rules) {
      totalWeight += rule.weight;

      const ruleViolations = await this.validateRule(rule, testSuite);

      if (ruleViolations.length === 0) {
        achievedWeight += rule.weight;
      } else {
        violations.push(...ruleViolations);
      }

      // Fail fast if violations exceed threshold
      if (violations.length > this.config.fail_fast_violations) {
        break;
      }
    }

    const complianceScore = totalWeight > 0 ? achievedWeight / totalWeight : 0;
    const passed = complianceScore >= this.config.compliance_threshold;

    return {
      timestamp: new Date().toISOString(),
      iteration: this.iteration,
      violations_found: violations,
      corrections_applied: [],
      compliance_score: complianceScore,
      passed: passed,
      execution_time_ms: Date.now() - this.startTime,
      escalation_triggered: false,
    };
  }

  /**
   * Validate test suite against a specific compliance rule
   */
  private async validateRule(rule: ComplianceRule, testSuite: TestSuite): Promise<Violation[]> {
    const violations: Violation[] = [];

    switch (rule.id) {
      case 'R1': // Coverage completeness
        // Check if all public methods have tests
        if (testSuite.metadata.total_tests === 0) {
          violations.push({
            rule_id: rule.id,
            rule_name: rule.name,
            severity: rule.severity,
            description: 'No tests generated for module',
            suggestion: 'Generate comprehensive test coverage',
          });
        }
        break;

      case 'R2': // Test independence
        // Check for shared state or dependencies
        for (const test of testSuite.tests) {
          if (test.code.includes('global ') || test.code.includes('shared_')) {
            violations.push({
              rule_id: rule.id,
              rule_name: rule.name,
              severity: rule.severity,
              description: `Test ${test.name} may have shared state`,
              location: test.name,
              suggestion: 'Use fixtures or setup/teardown for isolation',
            });
          }
        }
        break;

      case 'R3': // Naming convention
        for (const test of testSuite.tests) {
          if (!test.name.match(/^test_should_.*_when_.*$/)) {
            violations.push({
              rule_id: rule.id,
              rule_name: rule.name,
              severity: rule.severity,
              description: `Test name "${test.name}" doesn't follow convention`,
              location: test.name,
              suggestion: 'Use pattern: test_should_{action}_when_{condition}',
            });
          }
        }
        break;

      case 'R4': // Assertion presence
        for (const test of testSuite.tests) {
          if (test.assertions < 1) {
            violations.push({
              rule_id: rule.id,
              rule_name: rule.name,
              severity: rule.severity,
              description: `Test ${test.name} has no assertions`,
              location: test.name,
              suggestion: 'Add at least one assertion to verify behavior',
            });
          }
        }
        break;

      case 'R5': // Resource cleanup
        for (const test of testSuite.tests) {
          if (!test.code.includes('cleanup') && !test.code.includes('teardown')) {
            violations.push({
              rule_id: rule.id,
              rule_name: rule.name,
              severity: rule.severity,
              description: `Test ${test.name} missing cleanup`,
              location: test.name,
              suggestion: 'Add teardown or cleanup method',
            });
          }
        }
        break;

      case 'R7': {
        // Edge case coverage
        const requiredCases = rule.required_cases || [];
        const allCasesCovered = testSuite.tests.flatMap((t) => t.edge_cases_covered);

        for (const requiredCase of requiredCases) {
          if (!allCasesCovered.includes(requiredCase)) {
            violations.push({
              rule_id: rule.id,
              rule_name: rule.name,
              severity: rule.severity,
              description: `Missing edge case: ${requiredCase}`,
              suggestion: `Add test for ${requiredCase} condition`,
            });
          }
        }
        break;
      }

      case 'R10': // Integration ratio (80/20 rule)
        if (testSuite.metadata.integration_ratio < rule.min_integration_ratio) {
          violations.push({
            rule_id: rule.id,
            rule_name: rule.name,
            severity: rule.severity,
            description: `Integration ratio ${(testSuite.metadata.integration_ratio * 100).toFixed(1)}% below required ${rule.min_integration_ratio * 100}%`,
            suggestion: 'Add more integration tests to meet 80/20 doctrine',
          });
        }
        break;

      // Add more rule validations as needed
    }

    return violations;
  }

  // ==========================================================================
  // SELF-CORRECTION
  // ==========================================================================

  /**
   * Self-correct test suite based on violations
   * No external coordination - internal correction logic
   */
  private async selfCorrect(testSuite: TestSuite, violations: Violation[]): Promise<TestSuite> {
    const corrections: string[] = [];

    for (const violation of violations) {
      switch (violation.rule_id) {
        case 'R3': // Fix naming convention
          if (violation.location) {
            const test = testSuite.tests.find((t) => t.name === violation.location);
            if (test) {
              test.name = this.correctTestName(test.name);
              corrections.push(`Renamed ${violation.location} to ${test.name}`);
            }
          }
          break;

        case 'R4': // Add missing assertions
          if (violation.location) {
            const test = testSuite.tests.find((t) => t.name === violation.location);
            if (test) {
              test.assertions = Math.max(1, test.assertions);
              test.code += '\n    assert result is not None  # Added assertion';
              corrections.push(`Added assertion to ${violation.location}`);
            }
          }
          break;

        case 'R5': // Add cleanup
          if (violation.location) {
            const test = testSuite.tests.find((t) => t.name === violation.location);
            if (test) {
              test.code += '\n    # Teardown\n    cleanup()';
              corrections.push(`Added cleanup to ${violation.location}`);
            }
          }
          break;

        case 'R7': {
          // Add missing edge cases
          const missingCase = violation.description.match(/Missing edge case: (\w+)/)?.[1];
          if (missingCase) {
            const edgeCaseTest = await this.generateEdgeCaseTest(missingCase, testSuite.module);
            testSuite.tests.push(edgeCaseTest);
            corrections.push(`Added edge case test for ${missingCase}`);
          }
          break;
        }

        case 'R10': {
          // Add integration tests to meet 80/20
          const additionalIntegrationTests = await this.generateIntegrationTests(testSuite.module);
          testSuite.tests.push(...additionalIntegrationTests.slice(0, 2)); // Add 2 more
          corrections.push('Added integration tests to meet 80/20 ratio');
          break;
        }
      }
    }

    // Recalculate metadata
    const integrationCount = testSuite.tests.filter((t) => t.type === 'integration').length;
    const totalCount = testSuite.tests.length;

    testSuite.metadata = {
      total_tests: totalCount,
      integration_tests: integrationCount,
      unit_tests: totalCount - integrationCount,
      integration_ratio: totalCount > 0 ? integrationCount / totalCount : 0,
    };

    return testSuite;
  }

  private correctTestName(originalName: string): string {
    // Simple name correction - in production, use smarter logic
    if (originalName.startsWith('test_')) {
      const remainder = originalName.slice(5);
      return `test_should_${remainder}_when_condition`;
    }
    return `test_should_${originalName}_when_condition`;
  }

  private async generateEdgeCaseTest(edgeCase: string, module: string): Promise<Test> {
    return {
      name: `test_should_handle_${edgeCase}_when_${edgeCase}_input`,
      type: 'unit',
      code: this.generateUnitTestCode(edgeCase, module),
      assertions: 1,
      purpose: `Handle ${edgeCase} edge case`,
      edge_cases_covered: [edgeCase],
    };
  }

  // ==========================================================================
  // UTILITIES
  // ==========================================================================

  private isTimedOut(): boolean {
    const elapsed = (Date.now() - this.startTime) / 1000;
    return elapsed >= this.config.timeout_seconds;
  }

  /**
   * Generate audit trail for compliance decisions
   */
  private async generateAuditTrail(report: ComplianceReport): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = this.config.audit.filename_pattern.replace('{timestamp}', timestamp);
    const auditDir = path.resolve(__dirname, this.config.audit.output_dir);

    // Ensure logs directory exists
    if (!fs.existsSync(auditDir)) {
      fs.mkdirSync(auditDir, { recursive: true });
    }

    const filepath = path.join(auditDir, filename);

    const auditData = {
      version: this.config.version,
      generated_at: report.timestamp,
      total_iterations: report.iteration,
      final_compliance_score: report.compliance_score,
      passed: report.passed,
      violations_found: report.violations_found,
      corrections_applied: report.corrections_applied,
      execution_time_ms: report.execution_time_ms,
      escalation_triggered: report.escalation_triggered,
      escalation_reason: report.escalation_reason,
      Claude_Code_6_integration: this.config.Claude_Code_6_integration,
    };

    fs.writeFileSync(filepath, JSON.stringify(auditData, null, 2), 'utf-8');

    return filepath;
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export default TDDRedPhaseAgent;

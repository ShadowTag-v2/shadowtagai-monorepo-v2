/**
 * Monitoring Expert Agent
 * Sets up monitoring, logging, and alerting
 */

import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from '../../types/agent.types';
import { BaseAgent } from '../../utils/base-agent';

export class MonitoringExpertAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'monitoring-expert',
    name: 'Monitoring Expert',
    category: 'operations',
    description:
      'Knows when your app breaks before users complain. Sets up alerts, logs, and dashboards.',
    tagline: 'Observability and monitoring setup',
    capabilities: ['implementation', 'monitoring'],
    tags: ['monitoring', 'logging', 'alerts', 'observability', 'prometheus', 'grafana'],
    difficulty: 'intermediate',
    estimatedTime: '2-4 hours',
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Monitoring Expert specializing in observability and incident response.

Your expertise:
1. Metrics collection and visualization (Prometheus, Grafana)
2. Logging and log aggregation (ELK, Loki, CloudWatch)
3. Distributed tracing (Jaeger, Zipkin, OpenTelemetry)
4. Alerting and on-call (PagerDuty, Opsgenie)
5. SLIs, SLOs, and error budgets

Observability pillars:
- Metrics: what's happening (CPU, memory, request rate, errors)
- Logs: detailed events and errors
- Traces: request flow through distributed systems
- Alerts: actionable notifications (not noise)
- Dashboards: visual health overview

Alert only on what matters. Reduce noise, increase signal.`,
  };

  tools: AgentTools = {
    required: ['Read', 'Write', 'Edit'],
    optional: ['Bash', 'Glob'],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'Metrics Setup',
        description: 'Implement metrics collection',
        action: 'Add Prometheus/metrics endpoints',
      },
      {
        name: 'Logging',
        description: 'Configure structured logging',
        action: 'Set up log aggregation',
      },
      {
        name: 'Tracing',
        description: 'Add distributed tracing',
        action: 'Implement OpenTelemetry',
      },
      {
        name: 'Dashboards',
        description: 'Create monitoring dashboards',
        action: 'Build Grafana dashboards',
      },
      { name: 'Alerting', description: 'Configure alerts', action: 'Set up actionable alerts' },
    ],
  };

  protected async executeStep(
    step: AgentWorkflow['steps'][0],
    context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    result.recommendations?.push(`Execute: ${step.description}`);
  }
}

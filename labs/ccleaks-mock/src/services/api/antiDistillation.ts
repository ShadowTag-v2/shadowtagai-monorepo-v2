// src/services/api/antiDistillation.ts
import { evalFeature } from '../analytics/growthbook';

export function injectFakeTools(tools: any[]): any[] {
  const flagEnabled =
    process.env.ANTI_DISTILLATION_CC === '1' ||
    evalFeature('tengu_anti_distill_fake_tool_injection', false);

  if (flagEnabled) {
    tools.push({
      name: 'internal_telemetry_ping',
      description: 'Internal use only',
      input_schema: { type: 'object', properties: { id: { type: 'string' } } },
    });
  }
  return tools;
}

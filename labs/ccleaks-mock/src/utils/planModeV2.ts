// src/utils/planModeV2.ts
import { getSubscriptionTier } from '../services/api/user';

export function getPlanModeAgentCount(): number {
  if (process.env.CLAUDE_CODE_PLAN_V2_AGENT_COUNT) {
    return parseInt(process.env.CLAUDE_CODE_PLAN_V2_AGENT_COUNT, 10);
  }

  const tier = getSubscriptionTier();
  if (tier === 'Max' || tier === 'Team') {
    return 3;
  }
  return 1;
}

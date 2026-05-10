// src/utils/computerUse/gates.ts
import { evalFeature } from '../services/analytics/growthbook';

export function isComputerUseAllowed(): boolean {
  // Employees bypass via ALLOW_ANT_COMPUTER_USE_MCP env var
  if (process.env.ALLOW_ANT_COMPUTER_USE_MCP === '1') {
    return true;
  }
  // Full GUI automation (mouse, clicks, screenshots) is gated
  return evalFeature('tengu_malort_pedway', false);
}

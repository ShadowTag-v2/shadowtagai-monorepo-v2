// src/voice/voiceModeEnabled.ts
import { evalFeature } from '../services/analytics/growthbook';

export function isVoiceModeEnabled(): boolean {
  // Emergency off-switch
  if (evalFeature('tengu_amber_quartz_disabled', false)) {
    return false;
  }
  
  // OAuth auth required
  // ... check oauth state
  
  return true;
}

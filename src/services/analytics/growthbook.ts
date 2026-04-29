const featureCache = new Map<string, boolean>();

export function evalFeature(flagKey: string, defaultValue: boolean): boolean {
  if (process.env.CLAUDE_INTERNAL_FC_OVERRIDES === '1') {
    if (flagKey === 'tengu_malort_pedway') return true;
  }
  if (featureCache.has(flagKey)) {
    return featureCache.get(flagKey)!;
  }
  return defaultValue;
}

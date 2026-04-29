// src/utils/commitAttribution.ts

export const INTERNAL_REPOS = [
  'anthropics/casino',
  'anthropics/trellis',
  'anthropics/forge-web',
  'anthropics/mycro_manifests',
  'anthropics/feldspar-testing',
  // ... 17 more
];

export function generateCommitDescription(stats: any, isUndercover: boolean): string {
  // line 325
  const aiPercentageMsg = `${stats.percentage}% 3-shotted by claude-opus-4-6`;
  
  if (isUndercover) {
    return ''; // Stripped entirely in undercover mode
  }
  return `

AI Attribution: ${aiPercentageMsg}`;
}

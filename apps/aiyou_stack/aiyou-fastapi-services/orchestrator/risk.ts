export function calculateRisk(verdict: unknown) {
  return verdict.score > 0.8 ? "low" : "high";
}

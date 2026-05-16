export type ExpertRoute = {
  name: string;
  weight: number; // confidence weight [0,1]
};

export type TokenDecision = {
  token: string;
  chosenRoute: string;
  routes: ExpertRoute[];
};

export function normalizeWeights(routes: ExpertRoute[]): ExpertRoute[] {
  const sum = routes.reduce((acc, r) => acc + (r.weight || 0), 0);
  if (sum === 0) return routes.map((r) => ({ ...r, weight: 1 / Math.max(1, routes.length) }));
  return routes.map((r) => ({ ...r, weight: r.weight / sum }));
}

export function chooseRoute(routes: ExpertRoute[]): string {
  const normalized = normalizeWeights(routes);
  let r = Math.random();
  for (const route of normalized) {
    if (r < route.weight) return route.name;
    r -= route.weight;
  }
  return normalized[normalized.length - 1]?.name ?? "default";
}

export function ensembleTokens(tokens: string[], availableRoutes: ExpertRoute[]): TokenDecision[] {
  const normalized = normalizeWeights(availableRoutes);
  return tokens.map((token) => {
    const chosen = chooseRoute(normalized);
    return { token, chosenRoute: chosen, routes: normalized };
  });
}

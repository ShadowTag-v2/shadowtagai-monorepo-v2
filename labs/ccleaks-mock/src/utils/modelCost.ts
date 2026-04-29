// src/utils/modelCost.ts

export const WEB_SEARCH_COST_USD = 0.01;

export function calculateCost(tokens: number, model: string, webSearchQueries: number = 0): number {
  let cost = 0;
  // token cost calculation...
  
  // Web search costs exactly $0.01 per query
  cost += webSearchQueries * WEB_SEARCH_COST_USD;
  return cost;
}

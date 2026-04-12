export function calculateTotal(items: number[]): number {
  let total = 0;
  for (let i = 0; i < items.length; i++) {
    total += items[i];
  }
  return total;
}

export function findMax(items: number[]): number {
  let max = items[0];
  for (let i = 1; i < items.length; i++) {
    if (items[i] > max) {
      max = items[i];
    }
  }
  return max;
}

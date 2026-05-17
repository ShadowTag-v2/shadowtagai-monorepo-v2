/**
 * Pure utility functions — no side effects, no imports from services.
 */

/**
 * Formats a number with commas for display (e.g., 1234567 → "1,234,567").
 */
export function formatNumber(n: number): string {
  return n.toLocaleString("en-US");
}

/**
 * Formats a currency amount for display (e.g., 14900 cents → "$149.00").
 */
export function formatCurrency(cents: number, currency: string = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
  }).format(cents / 100);
}

/**
 * Truncates a string to the given length, appending "…" if truncated.
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return `${str.slice(0, maxLength - 1)}…`;
}

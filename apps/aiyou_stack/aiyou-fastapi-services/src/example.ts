/**
 * Example module to demonstrate test generation
 *
 * This file contains various functions that showcase different testing scenarios
 */

/**
 * Calculates the sum of two numbers
 */
export function add(a: number, b: number): number {
  if (typeof a !== 'number' || typeof b !== 'number') {
    throw new Error('Both arguments must be numbers');
  }
  return a + b;
}

/**
 * Calculates the product of two numbers
 */
export function multiply(a: number, b: number): number {
  if (typeof a !== 'number' || typeof b !== 'number') {
    throw new Error('Both arguments must be numbers');
  }
  return a * b;
}

/**
 * Divides two numbers
 */
export function divide(a: number, b: number): number {
  if (typeof a !== 'number' || typeof b !== 'number') {
    throw new Error('Both arguments must be numbers');
  }
  if (b === 0) {
    throw new Error('Cannot divide by zero');
  }
  return a / b;
}

/**
 * Async function that fetches user data
 */
export async function fetchUser(id: string): Promise<{ id: string; name: string }> {
  if (!id) {
    throw new Error('User ID is required');
  }

  // Simulate API call
  await new Promise((resolve) => setTimeout(resolve, 100));

  return {
    id,
    name: `User ${id}`,
  };
}

/**
 * Class demonstrating object-oriented code
 */
export class Calculator {
  private history: number[] = [];

  add(a: number, b: number): number {
    const result = a + b;
    this.history.push(result);
    return result;
  }

  subtract(a: number, b: number): number {
    const result = a - b;
    this.history.push(result);
    return result;
  }

  getHistory(): number[] {
    return [...this.history];
  }

  clearHistory(): void {
    this.history = [];
  }
}

/**
 * Validates email format
 */
export function isValidEmail(email: string): boolean {
  if (!email || typeof email !== 'string') {
    return false;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Formats a date to a readable string
 */
export function formatDate(date: Date, format: 'short' | 'long' = 'short'): string {
  if (!(date instanceof Date) || isNaN(date.getTime())) {
    throw new Error('Invalid date');
  }

  if (format === 'short') {
    return date.toLocaleDateString();
  } else {
    return date.toLocaleString();
  }
}

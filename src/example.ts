/**
 * Example module — canonical implementation backing tests/unit/example.test.ts
 *
 * These functions fulfill the contract defined by the test suite.
 * Do NOT remove without also removing the corresponding test file.
 */

// ─── Pure Math Functions ───

export function add(a: number, b: number): number {
  if (typeof a !== "number" || typeof b !== "number") {
    throw new Error("Both arguments must be numbers");
  }
  return a + b;
}

export function multiply(a: number, b: number): number {
  if (typeof a !== "number" || typeof b !== "number") {
    throw new Error("Both arguments must be numbers");
  }
  return a * b;
}

export function divide(a: number, b: number): number {
  if (typeof a !== "number" || typeof b !== "number") {
    throw new Error("Both arguments must be numbers");
  }
  if (b === 0) {
    throw new Error("Cannot divide by zero");
  }
  return a / b;
}

// ─── Async Functions ───

export interface User {
  id: string;
  name: string;
}

export async function fetchUser(id: string): Promise<User> {
  if (!id) {
    throw new Error("User ID is required");
  }
  // Simulate async fetch with minimal delay
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ id, name: `User ${id}` });
    }, 10);
  });
}

// ─── Calculator Class ───

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

// ─── Validation Functions ───

export function isValidEmail(email: unknown): boolean {
  if (typeof email !== "string" || !email) {
    return false;
  }
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// ─── Date Functions ───

export function formatDate(date: Date, format: "short" | "long" = "short"): string {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
    throw new Error("Invalid date");
  }
  if (format === "long") {
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }
  return date.toLocaleDateString("en-US");
}

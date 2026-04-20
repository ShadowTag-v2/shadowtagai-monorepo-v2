/**
 * Test Utilities and Helpers
 *
 * Common utilities for writing tests across the project
 */

import { jest } from '@jest/globals';

/**
 * Creates a mock function with type safety
 */
export function createMock<T extends (...args: unknown[]) => any>(): jest.MockedFunction<T> {
  return jest.fn() as jest.MockedFunction<T>;
}

/**
 * Waits for a condition to be true with timeout
 */
export async function waitFor(
  condition: () => boolean | Promise<boolean>,
  timeout: number = 5000,
  interval: number = 100,
): Promise<void> {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return;
    }
    await sleep(interval);
  }

  throw new Error(`Timeout waiting for condition after ${timeout}ms`);
}

/**
 * Sleep utility for async tests
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Creates a spy on an object method
 */
export function createSpy<T extends object, K extends keyof T>(
  obj: T,
  method: K,
): jest.SpyInstance {
  return jest.spyOn(obj, method as any);
}

/**
 * Generates random test data
 */
export const testData = {
  randomString: (length: number = 10): string => {
    return Math.random()
      .toString(36)
      .substring(2, length + 2);
  },

  randomNumber: (min: number = 0, max: number = 100): number => {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  },

  randomEmail: (): string => {
    return `test-${testData.randomString()}@example.com`;
  },

  randomDate: (start?: Date, end?: Date): Date => {
    const startTime = start?.getTime() || Date.now() - 365 * 24 * 60 * 60 * 1000;
    const endTime = end?.getTime() || Date.now();
    return new Date(startTime + Math.random() * (endTime - startTime));
  },

  randomBoolean: (): boolean => {
    return Math.random() > 0.5;
  },
};

/**
 * Test fixtures builder
 */
export class FixtureBuilder<T> {
  private defaults: Partial<T> = {};
  private overrides: Partial<T> = {};

  constructor(defaults: Partial<T>) {
    this.defaults = defaults;
  }

  with(overrides: Partial<T>): this {
    this.overrides = { ...this.overrides, ...overrides };
    return this;
  }

  build(): T {
    return { ...this.defaults, ...this.overrides } as T;
  }

  buildMany(count: number): T[] {
    return Array.from({ length: count }, () => this.build());
  }
}

/**
 * Assertion helpers
 */
export const assertions = {
  /**
   * Asserts that an async function throws
   */
  async toThrowAsync(fn: () => Promise<any>, expected?: string | RegExp): Promise<void> {
    let error: Error | null = null;

    try {
      await fn();
    } catch (e) {
      error = e as Error;
    }

    if (!error) {
      throw new Error('Expected function to throw an error');
    }

    if (expected) {
      if (typeof expected === 'string') {
        if (!error.message.includes(expected)) {
          throw new Error(
            `Expected error message to include "${expected}", got "${error.message}"`,
          );
        }
      } else {
        if (!expected.test(error.message)) {
          throw new Error(`Expected error message to match ${expected}, got "${error.message}"`);
        }
      }
    }
  },

  /**
   * Asserts that a value is defined
   */
  toBeDefined<T>(value: T | undefined | null): asserts value is T {
    if (value === undefined || value === null) {
      throw new Error('Expected value to be defined');
    }
  },

  /**
   * Type guard assertion
   */
  toBeOfType<T>(value: unknown, guard: (val: unknown) => val is T): asserts value is T {
    if (!guard(value)) {
      throw new Error('Type guard failed');
    }
  },
};

/**
 * Mock data generators
 */
export const mockData = {
  user: (overrides?: unknown) => ({
    id: testData.randomString(8),
    name: 'Test User',
    email: testData.randomEmail(),
    createdAt: new Date(),
    ...overrides,
  }),

  apiResponse: <T>(data: T, overrides?: unknown) => ({
    success: true,
    data,
    timestamp: new Date().toISOString(),
    ...overrides,
  }),

  error: (message: string = 'Test error', code: number = 500) => ({
    success: false,
    error: {
      message,
      code,
      timestamp: new Date().toISOString(),
    },
  }),
};

/**
 * Test database helpers
 */
export const dbHelpers = {
  /**
   * Clears all test data from database
   */
  async clearAll(): Promise<void> {
    // Implementation depends on database
    console.log('Clear all test data');
  },

  /**
   * Seeds test data
   */
  async seed(data: unknown): Promise<void> {
    console.log('Seed test data', data);
  },

  /**
   * Creates a transaction for test isolation
   */
  async transaction<T>(fn: () => Promise<T>): Promise<T> {
    // Begin transaction
    try {
      const result = await fn();
      // Rollback transaction (for tests)
      return result;
    } catch (error) {
      // Rollback transaction
      throw error;
    }
  },
};

/**
 * Performance testing helpers
 */
export const performance = {
  /**
   * Measures execution time
   */
  async measure<T>(fn: () => Promise<T>): Promise<{ result: T; duration: number }> {
    const start = Date.now();
    const result = await fn();
    const duration = Date.now() - start;
    return { result, duration };
  },

  /**
   * Asserts execution time is within threshold
   */
  async assertTiming<T>(fn: () => Promise<T>, maxDuration: number): Promise<T> {
    const { result, duration } = await this.measure(fn);

    if (duration > maxDuration) {
      throw new Error(`Operation took ${duration}ms, expected less than ${maxDuration}ms`);
    }

    return result;
  },
};

/**
 * Snapshot testing helpers
 */
export const snapshot = {
  /**
   * Sanitizes data for snapshot testing
   */
  sanitize(data: unknown): unknown {
    if (data instanceof Date) {
      return '[Date]';
    }
    if (typeof data === 'object' && data !== null) {
      const sanitized: unknown = Array.isArray(data) ? [] : {};
      for (const key in data) {
        if (key === 'id' || key === 'createdAt' || key === 'updatedAt') {
          sanitized[key] = `[${key}]`;
        } else {
          sanitized[key] = snapshot.sanitize(data[key]);
        }
      }
      return sanitized;
    }
    return data;
  },
};

/**
 * Console spy helpers
 */
export const consoleSpy = {
  /**
   * Suppresses console output during tests
   */
  suppress(): jest.SpyInstance[] {
    return [
      jest.spyOn(console, 'log').mockImplementation(),
      jest.spyOn(console, 'error').mockImplementation(),
      jest.spyOn(console, 'warn').mockImplementation(),
    ];
  },

  /**
   * Restores console output
   */
  restore(spies: jest.SpyInstance[]): void {
    spies.forEach((spy) => spy.mockRestore());
  },
};

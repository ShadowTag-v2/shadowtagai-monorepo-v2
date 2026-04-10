/**
 * Example Unit Tests
 *
 * Demonstrates comprehensive unit testing patterns
 */

import { describe, it, expect, beforeEach } from '@jest/globals';
import {
  add,
  multiply,
  divide,
  fetchUser,
  Calculator,
  isValidEmail,
  formatDate,
} from '../../src/example';

describe('Math Functions', () => {
  describe('add', () => {
    it('should add two positive numbers', () => {
      // Arrange
      const a = 5;
      const b = 3;

      // Act
      const result = add(a, b);

      // Assert
      expect(result).toBe(8);
    });

    it('should add negative numbers', () => {
      expect(add(-5, -3)).toBe(-8);
    });

    it('should add zero', () => {
      expect(add(5, 0)).toBe(5);
      expect(add(0, 5)).toBe(5);
    });

    it('should throw error for non-numeric input', () => {
      expect(() => add('5' as any, 3)).toThrow('Both arguments must be numbers');
      expect(() => add(5, '3' as any)).toThrow('Both arguments must be numbers');
    });
  });

  describe('multiply', () => {
    it('should multiply two numbers', () => {
      expect(multiply(5, 3)).toBe(15);
    });

    it('should handle multiplication by zero', () => {
      expect(multiply(5, 0)).toBe(0);
    });

    it('should handle negative multiplication', () => {
      expect(multiply(-5, 3)).toBe(-15);
      expect(multiply(-5, -3)).toBe(15);
    });

    it('should throw error for non-numeric input', () => {
      expect(() => multiply(null as any, 3)).toThrow();
    });
  });

  describe('divide', () => {
    it('should divide two numbers', () => {
      expect(divide(10, 2)).toBe(5);
    });

    it('should handle decimal division', () => {
      expect(divide(5, 2)).toBe(2.5);
    });

    it('should throw error when dividing by zero', () => {
      expect(() => divide(10, 0)).toThrow('Cannot divide by zero');
    });

    it('should throw error for non-numeric input', () => {
      expect(() => divide(10, undefined as any)).toThrow();
    });
  });
});

describe('Async Functions', () => {
  describe('fetchUser', () => {
    it('should fetch user by id', async () => {
      // Arrange
      const userId = 'user-123';

      // Act
      const user = await fetchUser(userId);

      // Assert
      expect(user).toBeDefined();
      expect(user.id).toBe(userId);
      expect(user.name).toBe('User user-123');
    });

    it('should throw error for empty id', async () => {
      await expect(fetchUser('')).rejects.toThrow('User ID is required');
    });

    it('should complete within reasonable time', async () => {
      const start = Date.now();
      await fetchUser('test-id');
      const duration = Date.now() - start;

      expect(duration).toBeLessThan(200);
    }, 1000);
  });
});

describe('Calculator Class', () => {
  let calculator: Calculator;

  beforeEach(() => {
    calculator = new Calculator();
  });

  describe('add', () => {
    it('should add numbers and track history', () => {
      const result = calculator.add(5, 3);

      expect(result).toBe(8);
      expect(calculator.getHistory()).toContain(8);
    });
  });

  describe('subtract', () => {
    it('should subtract numbers and track history', () => {
      const result = calculator.subtract(10, 3);

      expect(result).toBe(7);
      expect(calculator.getHistory()).toContain(7);
    });
  });

  describe('history', () => {
    it('should track multiple operations', () => {
      calculator.add(5, 3);
      calculator.subtract(10, 2);
      calculator.add(1, 1);

      const history = calculator.getHistory();
      expect(history).toHaveLength(3);
      expect(history).toEqual([8, 8, 2]);
    });

    it('should clear history', () => {
      calculator.add(5, 3);
      calculator.clearHistory();

      expect(calculator.getHistory()).toHaveLength(0);
    });

    it('should return a copy of history', () => {
      calculator.add(5, 3);
      const history = calculator.getHistory();
      history.push(999);

      expect(calculator.getHistory()).not.toContain(999);
    });
  });
});

describe('Validation Functions', () => {
  describe('isValidEmail', () => {
    it('should validate correct email format', () => {
      expect(isValidEmail('test@example.com')).toBe(true);
      expect(isValidEmail('user.name@domain.co.uk')).toBe(true);
    });

    it('should reject invalid email formats', () => {
      expect(isValidEmail('invalid')).toBe(false);
      expect(isValidEmail('invalid@')).toBe(false);
      expect(isValidEmail('@invalid.com')).toBe(false);
      expect(isValidEmail('invalid@domain')).toBe(false);
    });

    it('should handle edge cases', () => {
      expect(isValidEmail('')).toBe(false);
      expect(isValidEmail(null as any)).toBe(false);
      expect(isValidEmail(undefined as any)).toBe(false);
    });
  });
});

describe('Date Functions', () => {
  describe('formatDate', () => {
    const testDate = new Date('2025-01-15T12:00:00Z');

    it('should format date in short format', () => {
      const formatted = formatDate(testDate, 'short');
      expect(formatted).toBeTruthy();
      expect(typeof formatted).toBe('string');
    });

    it('should format date in long format', () => {
      const formatted = formatDate(testDate, 'long');
      expect(formatted).toBeTruthy();
      expect(typeof formatted).toBe('string');
      expect(formatted.length).toBeGreaterThan(0);
    });

    it('should use short format by default', () => {
      const short = formatDate(testDate);
      const explicit = formatDate(testDate, 'short');
      expect(short).toBe(explicit);
    });

    it('should throw error for invalid date', () => {
      expect(() => formatDate(new Date('invalid'))).toThrow('Invalid date');
      expect(() => formatDate({} as any)).toThrow('Invalid date');
    });
  });
});

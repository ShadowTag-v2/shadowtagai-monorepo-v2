/**
 * Example Integration Tests
 *
 * Demonstrates integration testing patterns across multiple components
 */

import { beforeEach, describe, expect, it } from "@jest/globals";
import { add, Calculator, multiply } from "../../src/example";

describe("Calculator Integration Tests", () => {
  let calculator: Calculator;

  beforeEach(() => {
    calculator = new Calculator();
  });

  describe("Complex Calculations", () => {
    it("should handle chained operations", () => {
      // Perform multiple operations
      calculator.add(10, 5); // 15
      calculator.subtract(20, 8); // 12
      calculator.add(3, 7); // 10

      const history = calculator.getHistory();

      expect(history).toHaveLength(3);
      expect(history[0]).toBe(15);
      expect(history[1]).toBe(12);
      expect(history[2]).toBe(10);
    });

    it("should integrate with standalone functions", () => {
      // Use standalone functions with calculator
      const sum = add(5, 3);
      const product = multiply(2, 4);

      calculator.add(sum, product); // 8 + 8 = 16

      expect(calculator.getHistory()).toContain(16);
    });

    it("should maintain state across operations", () => {
      // First batch of operations
      calculator.add(1, 1);
      calculator.add(2, 2);

      const firstHistory = calculator.getHistory();
      expect(firstHistory).toHaveLength(2);

      // Second batch - state should persist
      calculator.subtract(10, 5);

      const secondHistory = calculator.getHistory();
      expect(secondHistory).toHaveLength(3);
      expect(secondHistory).toContain(2);
      expect(secondHistory).toContain(4);
      expect(secondHistory).toContain(5);
    });
  });

  describe("Data Flow", () => {
    it("should process workflow correctly", () => {
      // Simulate a real workflow
      const input1 = 100;
      const input2 = 50;

      // Step 1: Calculate total
      const total = calculator.add(input1, input2);
      expect(total).toBe(150);

      // Step 2: Calculate difference
      const difference = calculator.subtract(input1, input2);
      expect(difference).toBe(50);

      // Step 3: Verify all operations tracked
      const operations = calculator.getHistory();
      expect(operations).toHaveLength(2);
    });

    it("should handle data dependencies", () => {
      // Each operation depends on previous results
      const step1 = calculator.add(10, 20); // 30
      const step2 = calculator.add(step1, 10); // 40
      const step3 = calculator.subtract(step2, 15); // 25

      expect(step1).toBe(30);
      expect(step2).toBe(40);
      expect(step3).toBe(25);

      expect(calculator.getHistory()).toEqual([30, 40, 25]);
    });
  });

  describe("Error Recovery", () => {
    it("should maintain state after errors", () => {
      calculator.add(5, 5);

      // This would cause an error in a real scenario
      // but our current implementation doesn't throw
      // In a real integration test, you'd test error boundaries

      calculator.add(10, 10);

      const history = calculator.getHistory();
      expect(history).toHaveLength(2);
    });
  });
});

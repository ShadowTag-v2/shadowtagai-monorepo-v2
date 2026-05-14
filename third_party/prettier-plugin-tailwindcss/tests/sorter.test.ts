import * as path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, test } from "vitest";
import { createSorter } from "../src/sorter";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

describe("createSorter", () => {
  describe("sortClassAttributes", () => {
    test("sorts with base + relative configPath (v3)", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/basic");
      const sorter = await createSorter({
        base: fixtureDir,
        filepath: path.join(fixtureDir, "index.html"),
        configPath: "./tailwind.config.js",
      });

      const [sorted] = sorter.sortClassAttributes(["sm:bg-tomato bg-red-500"]);
      expect(sorted).toBe("bg-red-500 sm:bg-tomato");
    });

    test("sorts with base + absolute configPath", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/basic");
      const configPath = path.join(fixtureDir, "tailwind.config.js");
      const sorter = await createSorter({
        base: fixtureDir,
        configPath,
      });

      const sorted = sorter.sortClassAttributes(["p-4 m-2", "hover:text-red-500 text-blue-500"]);
      expect(sorted).toEqual(["m-2 p-4", "text-blue-500 hover:text-red-500"]);
    });

    test("sorts with v4 stylesheet", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/custom-pkg-name-v4");
      const sorter = await createSorter({
        base: fixtureDir,
        stylesheetPath: "./app.css",
      });

      const [sorted] = sorter.sortClassAttributes(["sm:bg-tomato bg-red-500"]);
      expect(sorted).toBe("bg-red-500 sm:bg-tomato");
    });

    test("preserves whitespace when option is enabled", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/basic");
      const sorter = await createSorter({
        base: fixtureDir,
        configPath: "./tailwind.config.js",
        preserveWhitespace: true,
      });

      const [sorted] = sorter.sortClassAttributes(["  sm:bg-tomato   bg-red-500  "]);
      expect(sorted).toBe("  bg-red-500   sm:bg-tomato  ");
    });

    test("collapses whitespace by default", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/basic");
      const sorter = await createSorter({
        base: fixtureDir,
        configPath: "./tailwind.config.js",
      });

      const [sorted] = sorter.sortClassAttributes(["  sm:bg-tomato   bg-red-500  "]);
      expect(sorted).toBe("bg-red-500 sm:bg-tomato");
    });

    test("removes duplicates by default", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/basic");
      const sorter = await createSorter({
        base: fixtureDir,
        configPath: "./tailwind.config.js",
      });

      const [sorted] = sorter.sortClassAttributes(["bg-red-500 sm:bg-tomato bg-red-500"]);
      expect(sorted).toBe("bg-red-500 sm:bg-tomato");
    });

    test("preserves duplicates when option is enabled", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/basic");
      const sorter = await createSorter({
        base: fixtureDir,
        configPath: "./tailwind.config.js",
        preserveDuplicates: true,
      });

      const [sorted] = sorter.sortClassAttributes(["bg-red-500 sm:bg-tomato bg-red-500"]);
      expect(sorted).toBe("bg-red-500 bg-red-500 sm:bg-tomato");
    });
  });

  describe("sortClassLists", () => {
    test("sorts class lists (arrays of class names)", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/basic");
      const sorter = await createSorter({
        base: fixtureDir,
        configPath: "./tailwind.config.js",
      });

      const sorted = sorter.sortClassLists([
        ["sm:bg-tomato", "bg-red-500"],
        ["p-4", "m-2"],
      ]);

      expect(sorted).toEqual([
        ["bg-red-500", "sm:bg-tomato"],
        ["m-2", "p-4"],
      ]);
    });

    test("removes duplicates by default", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/basic");
      const sorter = await createSorter({
        base: fixtureDir,
        configPath: "./tailwind.config.js",
      });

      const [sorted] = sorter.sortClassLists([["bg-red-500", "sm:bg-tomato", "bg-red-500"]]);

      expect(sorted).toEqual(["bg-red-500", "sm:bg-tomato"]);
    });

    test("preserves duplicates when option is enabled", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/basic");
      const sorter = await createSorter({
        base: fixtureDir,
        configPath: "./tailwind.config.js",
        preserveDuplicates: true,
      });

      const [sorted] = sorter.sortClassLists([["bg-red-500", "sm:bg-tomato", "bg-red-500"]]);

      expect(sorted).toEqual(["bg-red-500", "bg-red-500", "sm:bg-tomato"]);
    });
  });

  describe("error handling", () => {
    test("handles auto-detection without explicit config", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/basic");
      const sorter = await createSorter({
        base: fixtureDir,
        filepath: path.join(fixtureDir, "index.html"),
      });

      const [sorted] = sorter.sortClassAttributes(["sm:bg-tomato bg-red-500"]);
      expect(sorted).toBe("bg-red-500 sm:bg-tomato");
    });

    test("works with no tailwind installation (uses bundled)", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/no-local-version");
      const sorter = await createSorter({
        base: fixtureDir,
        stylesheetPath: "./app.css",
      });

      const [sorted] = sorter.sortClassAttributes(["sm:bg-tomato bg-red-500"]);
      expect(sorted).toBe("bg-red-500 sm:bg-tomato");
    });

    test("works without a config file (uses default Tailwind config)", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/no-stylesheet-given");
      const sorter = await createSorter({
        base: fixtureDir,
      });

      // Should still sort using default Tailwind order
      const [sorted] = sorter.sortClassAttributes(["p-4 m-2"]);
      expect(sorted).toBe("m-2 p-4");
    });
  });

  describe("monorepo support", () => {
    test("resolves tailwind relative to filepath in monorepo", async () => {
      const fixtureDir = path.resolve(__dirname, "fixtures/monorepo");
      const package1Path = path.join(fixtureDir, "package-1", "index.html");

      const sorter = await createSorter({
        base: path.join(fixtureDir, "package-1"),
        filepath: package1Path,
        stylesheetPath: "./app.css",
      });

      const [sorted] = sorter.sortClassAttributes(["sm:bg-tomato bg-red-500"]);
      expect(sorted).toBe("bg-red-500 sm:bg-tomato");
    });
  });
});

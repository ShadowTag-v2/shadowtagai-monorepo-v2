import { beforeEach, describe, expect, mock, test } from "bun:test";
import { createMockRenderer } from "../../ui/mock-factory.ts";

mock.module("opentui-gameboy", () => ({
  launchGameboy: mock(() => {}),
  isGameboyActive: mock(() => true),
}));

import { isGameboyActive, launchGameboy } from "./GameboyView.js";

describe("GameboyView", () => {
  let mockRenderer: any;

  beforeEach(() => {
    mockRenderer = createMockRenderer();
  });

  test("should launch gameboy", () => {
    const options = {
      onExit: mock(() => {}),
    };
    launchGameboy(mockRenderer, options);
    expect(isGameboyActive()).toBe(true);
  });
});

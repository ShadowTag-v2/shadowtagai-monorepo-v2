/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { Box } from "ink";
import type React from "react";
import { describe, expect, it, vi } from "vitest";
import { render } from "../../test-utils/render.js";
import type { ConsoleMessageItem } from "../types.js";
import { DetailedMessagesDisplay } from "./DetailedMessagesDisplay.js";

vi.mock("./shared/ScrollableList.js", () => ({
  ScrollableList: ({
    data,
    renderItem,
  }: {
    data: unknown[];
    renderItem: (props: { item: unknown }) => React.ReactNode;
  }) => (
    <Box flexDirection="column">
      {data.map((item: unknown, index: number) => (
        <Box key={index}>{renderItem({ item })}</Box>
      ))}
    </Box>
  ),
}));

describe("DetailedMessagesDisplay", () => {
  it("renders nothing when messages are empty", () => {
    const { lastFrame } = render(
      <DetailedMessagesDisplay messages={[]} maxHeight={10} width={80} hasFocus={false} />,
    );
    expect(lastFrame()).toBe("");
  });

  it("renders messages correctly", () => {
    const messages: ConsoleMessageItem[] = [
      { type: "log", content: "Log message", count: 1 },
      { type: "warn", content: "Warning message", count: 1 },
      { type: "error", content: "Error message", count: 1 },
      { type: "debug", content: "Debug message", count: 1 },
    ];

    const { lastFrame } = render(
      <DetailedMessagesDisplay messages={messages} maxHeight={20} width={80} hasFocus={true} />,
    );
    const output = lastFrame();

    expect(output).toContain("Debug Console");
    expect(output).toContain("Log message");
    expect(output).toContain("Warning message");
    expect(output).toContain("Error message");
    expect(output).toContain("Debug message");

    // Check for icons
    expect(output).toContain("ℹ");
    expect(output).toContain("⚠");
    expect(output).toContain("✖");
    expect(output).toContain("🔍");
  });

  it("renders message counts", () => {
    const messages: ConsoleMessageItem[] = [{ type: "log", content: "Repeated message", count: 5 }];

    const { lastFrame } = render(
      <DetailedMessagesDisplay messages={messages} maxHeight={10} width={80} hasFocus={false} />,
    );
    const output = lastFrame();

    expect(output).toContain("Repeated message");
    expect(output).toContain("(x5)");
  });
});

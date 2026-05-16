#!/usr/bin/env node

/**
 * Judge #6 CLI Entry Point
 * Flicker-free TUI using Ink (alternate screen buffer automatic)
 */

import { render } from "ink";
import React from "react";
import { App } from "./components/App.js";

// Render app (Ink automatically uses alternate screen buffer)
const { unmount, waitUntilExit } = render(<App />);

// Handle graceful exit
process.on("SIGINT", () => {
  unmount();
  process.exit(0);
});

// Wait for exit
await waitUntilExit();

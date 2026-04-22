#!/usr/bin/env node

/**
 * Judge 6 CLI - Zero-Flicker TUI
 *
 * Entry point for the Judge 6 decision validation CLI.
 * Inspired by Google's Gemini CLI terminal rendering improvements.
 */

import { render } from 'ink';
import React from 'react';
import { DecisionReview } from './components/DecisionReview.js';

// Parse command-line arguments
const args = process.argv.slice(2);
const apiUrlArg = args.find((arg) => arg.startsWith('--api-url='));
const apiUrl = apiUrlArg ? apiUrlArg.split('=')[1] : 'http://localhost:8000';

// Show help
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
Judge 6 CLI - Decision Validation Tool

USAGE:
  judge6 [OPTIONS]

OPTIONS:
  --api-url=<url>    API endpoint (default: http://localhost:8000)
  --help, -h         Show this help message
  --version, -v      Show version

EXAMPLES:
  # Start with default API (localhost:8000)
  judge6

  # Connect to remote API
  judge6 --api-url=https://api.pnkln.com

  # Show version
  judge6 --version

ABOUT:
  Judge 6 validates decisions using the Purpose/Reasons/Brakes framework.
  All decisions must:
    1. PURPOSE: Advance the mission
    2. REASONS: Be defensible and logical
    3. BRAKES: Not cause catastrophic failure

  ATP 5-19 compliance: Decisions compressed to 487 bytes (95% reduction).

KEYBOARD SHORTCUTS:
  Ctrl+C             Exit application
  Enter              Submit decision for validation

DASHBOARD:
  View history and analytics at https://dashboard.pnkln.com
  Free tier: 100 decisions/month
  Pro tier: Unlimited + team collaboration ($49/mo)

MORE INFO:
  GitHub: https://github.com/ehanc69/shadowtag_v4-fastapi-services
  Docs: https://docs.pnkln.com/judge6-cli
`);
  process.exit(0);
}

// Show version
if (args.includes('--version') || args.includes('-v')) {
  console.log('Judge 6 CLI v2.0.0');
  process.exit(0);
}

// Render TUI (uses alternate screen buffer automatically)
render(<DecisionReview apiUrl={apiUrl} />);

/**
 * POST TOOL USE HOOK: File Edit Tracker
 *
 * Tracks all file edits, writes, and modifications to enable downstream hooks
 * to know which files/repos were changed without redundant analysis.
 *
 * Runs after: Edit, Write, MultiEdit, NotebookEdit operations
 *
 * Outputs: .claude/hooks/edited-files.json
 * Format: { timestamp, files: [{ path, repo, operation, tool }] }
 */

import type { Hook } from '@anthropic-ai/claude-agent-sdk';
import * as fs from 'fs';
import * as path from 'path';

const TRACKED_TOOLS = ['Edit', 'Write', 'MultiEdit', 'NotebookEdit'];
const OUTPUT_FILE = '.claude/hooks/edited-files.json';

export const hook: Hook = {
  name: 'post-tool-use-file-tracker',
  type: 'post-tool-use',
  async execute(context) {
    const { tool, parameters } = context;

    // Only track file modification tools
    if (!TRACKED_TOOLS.includes(tool)) {
      return { continue: true };
    }

    // Extract file path from different tool parameters
    let filePath: string | null = null;
    if (parameters.file_path) {
      filePath = parameters.file_path;
    } else if (parameters.notebook_path) {
      filePath = parameters.notebook_path;
    }

    if (!filePath) {
      return { continue: true };
    }

    // Determine repository (simplified - assumes single repo for now)
    const repo = 'ShadowTag-v2-fastapi-services';

    // Load existing edit log
    let editLog: any = { files: [] };
    if (fs.existsSync(OUTPUT_FILE)) {
      try {
        editLog = JSON.parse(fs.readFileSync(OUTPUT_FILE, 'utf-8'));
      } catch (e) {
        // If parsing fails, start fresh
        editLog = { files: [] };
      }
    }

    // Add new entry
    editLog.timestamp = new Date().toISOString();
    editLog.files.push({
      path: filePath,
      repo: repo,
      operation: tool,
      timestamp: new Date().toISOString(),
    });

    // Write updated log
    fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(editLog, null, 2));

    return { continue: true };
  },
};

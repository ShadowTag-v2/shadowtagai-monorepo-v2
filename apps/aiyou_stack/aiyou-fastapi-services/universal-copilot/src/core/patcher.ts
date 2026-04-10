/**
 * Unified diff patch application system
 * Safely applies code patches with validation and rollback
 */

import * as fs from "node:fs/promises";
import * as path from "node:path";
import { PatchError } from "./errors.js";

/**
 * Patch application result
 */
export interface PatchResult {
  success: boolean;
  filePath: string;
  linesChanged: number;
  backup?: string;
  error?: string;
}

/**
 * Patch application options
 */
export interface PatchOptions {
  createBackup?: boolean;
  dryRun?: boolean;
  validateSyntax?: boolean;
}

/**
 * Unified diff patcher
 */
export class UnifiedPatcher {
  /**
   * Apply a unified diff patch to a file
   */
  async applyPatch(
    filePath: string,
    unifiedDiff: string,
    options: PatchOptions = {},
  ): Promise<PatchResult> {
    const { createBackup = true, dryRun = false, validateSyntax = false } = options;

    try {
      // Read current file content
      const originalContent = await this.readFile(filePath);

      // Parse and apply diff
      const patchedContent = this.applyUnifiedDiff(originalContent, unifiedDiff, filePath);

      // Validate syntax if requested
      if (validateSyntax) {
        await this.validateSyntax(filePath, patchedContent);
      }

      let backup: string | undefined;

      if (!dryRun) {
        // Create backup if requested
        if (createBackup) {
          backup = await this.createBackup(filePath, originalContent);
        }

        // Write patched content
        await this.writeFile(filePath, patchedContent);
      }

      return {
        success: true,
        filePath,
        linesChanged: this.countChangedLines(originalContent, patchedContent),
        backup,
      };
    } catch (error: unknown) {
      return {
        success: false,
        filePath,
        linesChanged: 0,
        error: error.message,
      };
    }
  }

  /**
   * Apply unified diff format to content
   */
  private applyUnifiedDiff(original: string, diff: string, filePath: string): string {
    const lines = diff.split("\n");

    // Validate diff format
    if (!this.isValidDiff(lines, filePath)) {
      throw new PatchError("Invalid unified diff format");
    }

    // Extract hunks
    const hunks = this.parseHunks(lines);

    // Apply each hunk
    let result = original.split("\n");
    for (const hunk of hunks) {
      result = this.applyHunk(result, hunk);
    }

    return result.join("\n");
  }

  private isValidDiff(lines: string[], filePath: string): boolean {
    // Check for diff headers
    const hasOldMarker = lines.some((l) => l.startsWith("---") && l.includes(filePath));
    const hasNewMarker = lines.some((l) => l.startsWith("+++") && l.includes(filePath));
    const hasHunkMarker = lines.some((l) => l.startsWith("@@"));

    return hasOldMarker && hasNewMarker && hasHunkMarker;
  }

  private parseHunks(lines: string[]): Hunk[] {
    const hunks: Hunk[] = [];
    let currentHunk: Hunk | null = null;

    for (const line of lines) {
      if (line.startsWith("@@")) {
        // New hunk
        if (currentHunk) {
          hunks.push(currentHunk);
        }
        currentHunk = this.parseHunkHeader(line);
      } else if (currentHunk) {
        // Hunk content
        if (line.startsWith("-")) {
          currentHunk.removed.push(line.substring(1));
        } else if (line.startsWith("+")) {
          currentHunk.added.push(line.substring(1));
        } else if (line.startsWith(" ")) {
          // Context line (included in both)
          const content = line.substring(1);
          currentHunk.removed.push(content);
          currentHunk.added.push(content);
        }
      }
    }

    if (currentHunk) {
      hunks.push(currentHunk);
    }

    return hunks;
  }

  private parseHunkHeader(line: string): Hunk {
    // Parse: @@ -startLine,count +startLine,count @@
    const match = line.match(/@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@/);
    if (!match) {
      throw new PatchError(`Invalid hunk header: ${line}`);
    }

    return {
      oldStart: parseInt(match[1]),
      oldCount: parseInt(match[2] || "1"),
      newStart: parseInt(match[3]),
      newCount: parseInt(match[4] || "1"),
      removed: [],
      added: [],
    };
  }

  private applyHunk(lines: string[], hunk: Hunk): string[] {
    const result = [...lines];

    // Simple replacement strategy:
    // Remove old lines and insert new lines at the position
    const startIndex = hunk.oldStart - 1; // Convert to 0-based index

    // Remove old lines
    result.splice(startIndex, hunk.removed.length);

    // Insert new lines
    result.splice(startIndex, 0, ...hunk.added);

    return result;
  }

  /**
   * Restore from backup
   */
  async restore(filePath: string, backupPath: string): Promise<void> {
    try {
      const backupContent = await this.readFile(backupPath);
      await this.writeFile(filePath, backupContent);
      await fs.unlink(backupPath);
    } catch (error: unknown) {
      throw new PatchError(`Failed to restore from backup: ${error.message}`, {
        backupPath,
        filePath,
      });
    }
  }

  /**
   * List available backups for a file
   */
  async listBackups(filePath: string): Promise<string[]> {
    const dir = path.dirname(filePath);
    const basename = path.basename(filePath);
    const backupPattern = `${basename}.backup-`;

    try {
      const files = await fs.readdir(dir);
      return files
        .filter((f) => f.startsWith(backupPattern))
        .map((f) => path.join(dir, f))
        .sort()
        .reverse(); // Most recent first
    } catch {
      return [];
    }
  }

  private async createBackup(filePath: string, content: string): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const backupPath = `${filePath}.backup-${timestamp}`;

    await this.writeFile(backupPath, content);
    return backupPath;
  }

  private async readFile(filePath: string): Promise<string> {
    try {
      return await fs.readFile(filePath, "utf-8");
    } catch (error: unknown) {
      throw new PatchError(`Failed to read file: ${error.message}`, { filePath });
    }
  }

  private async writeFile(filePath: string, content: string): Promise<void> {
    try {
      // Ensure directory exists
      await fs.mkdir(path.dirname(filePath), { recursive: true });
      await fs.writeFile(filePath, content, "utf-8");
    } catch (error: unknown) {
      throw new PatchError(`Failed to write file: ${error.message}`, { filePath });
    }
  }

  private countChangedLines(original: string, patched: string): number {
    const originalLines = original.split("\n");
    const patchedLines = patched.split("\n");

    let changes = 0;
    const maxLen = Math.max(originalLines.length, patchedLines.length);

    for (let i = 0; i < maxLen; i++) {
      if (originalLines[i] !== patchedLines[i]) {
        changes++;
      }
    }

    return changes;
  }

  private async validateSyntax(filePath: string, content: string): Promise<void> {
    // Basic syntax validation (can be extended)
    const ext = path.extname(filePath);

    // For now, just check for basic issues
    if (ext === ".json") {
      try {
        JSON.parse(content);
      } catch {
        throw new PatchError("Invalid JSON syntax after patch");
      }
    }

    // Add more validators as needed
  }
}

/**
 * Hunk representation
 */
interface Hunk {
  oldStart: number;
  oldCount: number;
  newStart: number;
  newCount: number;
  removed: string[];
  added: string[];
}

/**
 * Create patcher instance
 */
export function createPatcher(): UnifiedPatcher {
  return new UnifiedPatcher();
}

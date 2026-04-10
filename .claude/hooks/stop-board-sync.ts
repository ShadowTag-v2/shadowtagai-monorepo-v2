/**
 * STOP HOOK: Board Automation Sync
 *
 * Parses task completion from *-tasks.md files and automatically updates
 * board status via board API. Enables "160-IQ board automation" where
 * checking off tasks in dev docs automatically updates project boards.
 *
 * Reads frontmatter from tasks.md:
 *   board_id: project-board-123
 *   epic: EPIC-456
 *   priority: High
 *   status: In Progress
 *
 * Parses checkbox completion:
 *   - [x] Completed task
 *   - [ ] Pending task
 *
 * POSTs updates to board API when:
 *   - Phase checkpoints completed
 *   - Overall task status changes
 *   - Priority/assignment changes
 */

import { Hook } from "@anthropic-ai/claude-agent-sdk";
import { execSync } from "child_process";
import * as fs from "fs";
import * as path from "path";
import * as yaml from "yaml"; // May need: npm install yaml

const DEV_DOCS_DIR = ".claude/dev/active";
const SYNC_LOG = ".claude/hooks/board-sync.log";

interface BoardMetadata {
  board_id?: string;
  epic?: string;
  priority?: string;
  assignee?: string;
  labels?: string[];
  status?: string;
}

interface TaskFile {
  path: string;
  content: string;
  metadata: BoardMetadata;
  completedTasks: number;
  totalTasks: number;
  completionRate: number;
}

export const hook: Hook = {
  name: "stop-board-sync",
  type: "stop",
  async execute(context) {
    // Check if dev docs directory exists
    if (!fs.existsSync(DEV_DOCS_DIR)) {
      return { continue: true };
    }

    const results: string[] = [];
    results.push("\n=== 📊 Board Automation Sync ===\n");

    try {
      // Find all *-tasks.md files in active dev docs
      const taskFiles = findTaskFiles(DEV_DOCS_DIR);

      if (taskFiles.length === 0) {
        return { continue: true };
      }

      results.push(`Found ${taskFiles.length} task file(s) to process\n`);

      // Process each task file
      for (const taskFile of taskFiles) {
        const syncResult = await syncTaskFileToBoard(taskFile);
        results.push(syncResult);
      }

      // Log sync results
      logSyncResults(results.join("\n"));

      // Display summary
      console.log(results.join("\n"));

      return { continue: true, message: results.join("\n") };
    } catch (e: any) {
      results.push(`⚠️  Board sync error: ${e.message}`);
      console.log(results.join("\n"));
      return { continue: true };
    }
  },
};

function findTaskFiles(dir: string): TaskFile[] {
  const taskFiles: TaskFile[] = [];

  if (!fs.existsSync(dir)) {
    return taskFiles;
  }

  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      // Recursively search subdirectories
      taskFiles.push(...findTaskFiles(fullPath));
    } else if (entry.isFile() && entry.name.endsWith("-tasks.md")) {
      // Parse task file
      const content = fs.readFileSync(fullPath, "utf-8");
      const metadata = extractMetadata(content);
      const { completed, total } = countTasks(content);

      taskFiles.push({
        path: fullPath,
        content,
        metadata,
        completedTasks: completed,
        totalTasks: total,
        completionRate: total > 0 ? (completed / total) * 100 : 0,
      });
    }
  }

  return taskFiles;
}

function extractMetadata(content: string): BoardMetadata {
  // Extract YAML frontmatter between ```yaml blocks
  const yamlMatch = content.match(/```yaml\n([\s\S]*?)\n```/);

  if (!yamlMatch) {
    return {};
  }

  try {
    // Parse YAML (requires yaml package: npm install yaml)
    // For now, use simple regex parsing
    const yamlContent = yamlMatch[1];
    const metadata: BoardMetadata = {};

    const lines = yamlContent.split("\n");
    for (const line of lines) {
      const [key, ...valueParts] = line.split(":");
      if (!key || !valueParts.length) continue;

      const value = valueParts.join(":").trim();

      if (key.trim() === "board_id") metadata.board_id = value;
      else if (key.trim() === "epic") metadata.epic = value;
      else if (key.trim() === "priority") metadata.priority = value;
      else if (key.trim() === "assignee") metadata.assignee = value;
      else if (key.trim() === "status") metadata.status = value;
      else if (key.trim() === "labels") {
        // Parse array: [label1, label2, label3]
        const labelsMatch = value.match(/\[(.*?)\]/);
        if (labelsMatch) {
          metadata.labels = labelsMatch[1].split(",").map((l) => l.trim());
        }
      }
    }

    return metadata;
  } catch (e) {
    return {};
  }
}

function countTasks(content: string): { completed: number; total: number } {
  // Count checkboxes
  const completedPattern = /^- \[x\]/gim;
  const pendingPattern = /^- \[ \]/gim;

  const completed = (content.match(completedPattern) || []).length;
  const pending = (content.match(pendingPattern) || []).length;
  const total = completed + pending;

  return { completed, total };
}

async function syncTaskFileToBoard(taskFile: TaskFile): Promise<string> {
  const results: string[] = [];

  const taskName = path.basename(taskFile.path, "-tasks.md");
  results.push(`\n📋 Task: ${taskName}`);

  // Check if board metadata exists
  if (!taskFile.metadata.board_id) {
    results.push(`   ⚠️  No board_id - skipping sync`);
    return results.join("\n");
  }

  results.push(`   Board: ${taskFile.metadata.board_id}`);

  if (taskFile.metadata.epic) {
    results.push(`   Epic: ${taskFile.metadata.epic}`);
  }

  results.push(
    `   Progress: ${taskFile.completedTasks}/${taskFile.totalTasks} (${taskFile.completionRate.toFixed(1)}%)`
  );

  // Determine status based on completion
  let newStatus = taskFile.metadata.status || "In Progress";

  if (taskFile.completionRate === 0) {
    newStatus = "To Do";
  } else if (taskFile.completionRate === 100) {
    newStatus = "Done";
  } else {
    newStatus = "In Progress";
  }

  // Check if status changed
  if (taskFile.metadata.status && taskFile.metadata.status !== newStatus) {
    results.push(`   Status: ${taskFile.metadata.status} → ${newStatus}`);

    // TODO: Call board API to update status
    // For now, just log the intended update
    results.push(`   ✅ Would update board (API integration pending)`);

    // Example API call (commented out - implement based on your board system):
    /*
    try {
      await updateBoardStatus({
        board_id: taskFile.metadata.board_id,
        epic: taskFile.metadata.epic,
        status: newStatus,
        completion_rate: taskFile.completionRate,
        labels: taskFile.metadata.labels
      });
      results.push(`   ✅ Board updated successfully`);
    } catch (e: any) {
      results.push(`   ❌ Board update failed: ${e.message}`);
    }
    */
  } else {
    results.push(`   Status: ${newStatus} (no change)`);
  }

  // Check for phase checkpoints
  const checkpoints = extractCheckpoints(taskFile.content);
  if (checkpoints.length > 0) {
    results.push(`   Checkpoints:`);
    for (const checkpoint of checkpoints) {
      results.push(`     - ${checkpoint.phase}: ${checkpoint.status}`);
    }
  }

  return results.join("\n");
}

interface Checkpoint {
  phase: string;
  status: "Pending" | "Complete";
  timestamp?: string;
}

function extractCheckpoints(content: string): Checkpoint[] {
  const checkpoints: Checkpoint[] = [];

  // Find checkpoint markers like "**Phase 1 Checkpoint**: [timestamp]"
  const checkpointPattern = /\*\*Phase (\d+) Checkpoint\*\*: (.+)/g;

  let match;
  while ((match = checkpointPattern.exec(content)) !== null) {
    const phase = `Phase ${match[1]}`;
    const timestamp = match[2].trim();

    checkpoints.push({
      phase,
      status: timestamp !== "[Completion date/time when done]" ? "Complete" : "Pending",
      timestamp: timestamp !== "[Completion date/time when done]" ? timestamp : undefined,
    });
  }

  return checkpoints;
}

function logSyncResults(results: string): void {
  const timestamp = new Date().toISOString();
  const logEntry = `\n[${timestamp}]\n${results}\n`;

  try {
    fs.appendFileSync(SYNC_LOG, logEntry);
  } catch (e) {
    // Ignore logging errors
  }
}

// Board API integration functions (implement based on your board system)

/*
interface BoardUpdatePayload {
  board_id: string;
  epic?: string;
  status: string;
  completion_rate: number;
  labels?: string[];
}

async function updateBoardStatus(payload: BoardUpdatePayload): Promise<void> {
  // Example: POST to board API
  const response = await fetch(`https://api.yourboard.com/v1/boards/${payload.board_id}/items`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.BOARD_API_TOKEN}`
    },
    body: JSON.stringify({
      epic_id: payload.epic,
      status: payload.status,
      progress: payload.completion_rate,
      labels: payload.labels
    })
  });

  if (!response.ok) {
    throw new Error(`Board API error: ${response.statusText}`);
  }
}
*/

/**
 * USER PROMPT SUBMIT HOOK: Skill Auto-Activator
 *
 * Analyzes user prompts before Claude processes them and injects skill suggestions
 * when triggers match. This solves Claude Code's #1 problem: skills sitting unused.
 *
 * Trigger dimensions:
 * - Keywords: Explicit topics (e.g., "vertex ai", "bigquery")
 * - Intent patterns: Regex matching actions (e.g., "create.*route", "train.*model")
 * - File patterns: Recently edited file locations (e.g., **/ ml/**/*
.py)
 * - Content patterns: Code patterns in recent files (e.g., "from google.cloud import")
 *
 * Loads skill-rules.json and injects formatted skill recommendations into Claude's context.
 */

import type { Hook } from '@anthropic-ai/claude-agent-sdk';
import * as fs from 'fs';
import * as path from 'path';

const SKILL_RULES_FILE = '.claude/skills/skill-rules.json';
const EDIT_LOG = '.claude/hooks/edited-files.json';

interface SkillTriggers {
  keywords?: string[];
  intent_patterns?: string[];
  file_patterns?: string[];
  content_patterns?: string[];
}

interface SkillRule {
  skill: string;
  triggers: SkillTriggers;
  priority: 'high' | 'medium' | 'low';
  description: string;
}

interface SkillRules {
  rules: SkillRule[];
}

interface EditLog {
  timestamp: string;
  files: Array<{ path: string }>;
}

export const hook: Hook = {
  name: 'user-prompt-submit-skill-activator',
  type: 'user-prompt-submit',
  async execute(context) {
    const { prompt } = context;

    // Load skill rules
    if (!fs.existsSync(SKILL_RULES_FILE)) {
      return { continue: true, prompt };
    }

    let skillRules: SkillRules;
    try {
      skillRules = JSON.parse(fs.readFileSync(SKILL_RULES_FILE, 'utf-8'));
    } catch (e) {
      console.error('Failed to parse skill-rules.json:', e);
      return { continue: true, prompt };
    }

    // Load recent file edits for context
    let recentFiles: string[] = [];
    if (fs.existsSync(EDIT_LOG)) {
      try {
        const editLog: EditLog = JSON.parse(fs.readFileSync(EDIT_LOG, 'utf-8'));
        recentFiles = editLog.files.map((f) => f.path);
      } catch (e) {
        // Ignore edit log parsing errors
      }
    }

    // Analyze prompt and match against skill triggers
    const matchedSkills: Array<{
      skill: string;
      priority: string;
      description: string;
      reasons: string[];
    }> = [];

    for (const rule of skillRules.rules) {
      const reasons: string[] = [];

      // Check keyword matches
      if (rule.triggers.keywords) {
        const promptLower = prompt.toLowerCase();
        for (const keyword of rule.triggers.keywords) {
          if (promptLower.includes(keyword.toLowerCase())) {
            reasons.push(`keyword: "${keyword}"`);
            break;
          }
        }
      }

      // Check intent pattern matches
      if (rule.triggers.intent_patterns) {
        for (const pattern of rule.triggers.intent_patterns) {
          const regex = new RegExp(pattern, 'i');
          if (regex.test(prompt)) {
            reasons.push(`intent: "${pattern}"`);
            break;
          }
        }
      }

      // Check file pattern matches against recent edits
      if (rule.triggers.file_patterns && recentFiles.length > 0) {
        for (const filePattern of rule.triggers.file_patterns) {
          // Convert glob pattern to regex (simplified)
          const regexPattern = filePattern
            .replace(/\*\*/g, '.*')
            .replace(/\*/g, '[^/]*')
            .replace(/\?/g, '.');

          const regex = new RegExp(regexPattern);

          for (const file of recentFiles) {
            if (regex.test(file)) {
              reasons.push(`file pattern: "${filePattern}"`);
              break;
            }
          }
          if (reasons.length > 0) break;
        }
      }

      // If any triggers matched, add skill to recommendations
      if (reasons.length > 0) {
        matchedSkills.push({
          skill: rule.skill,
          priority: rule.priority,
          description: rule.description,
          reasons,
        });
      }
    }

    // If no skills matched, return original prompt
    if (matchedSkills.length === 0) {
      return { continue: true, prompt };
    }

    // Sort by priority (high > medium > low)
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    matchedSkills.sort(
      (a, b) =>
        priorityOrder[a.priority as keyof typeof priorityOrder] -
        priorityOrder[b.priority as keyof typeof priorityOrder],
    );

    // Format skill recommendations
    const recommendations: string[] = [];
    recommendations.push('\n=== 💡 Skill Recommendations (Auto-Activated) ===\n');
    recommendations.push('The following skills may be relevant for this task:\n');

    for (const match of matchedSkills) {
      recommendations.push(`**${match.skill}** (${match.priority} priority)`);
      recommendations.push(`  ${match.description}`);
      recommendations.push(`  Triggered by: ${match.reasons.join(', ')}`);
      recommendations.push(`  Consider loading: /skill ${match.skill}`);
      recommendations.push('');
    }

    recommendations.push('=== End Skill Recommendations ===\n');

    // Inject recommendations into prompt
    const enhancedPrompt = recommendations.join('\n') + '\n' + prompt;

    return { continue: true, prompt: enhancedPrompt };
  },
};

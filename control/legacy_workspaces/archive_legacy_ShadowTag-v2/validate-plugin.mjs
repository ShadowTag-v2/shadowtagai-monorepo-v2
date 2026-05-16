#!/usr/bin/env node
/**
 * Plugin Structure Validator
 * Validates erik-interaction plugin structure and configuration
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const pluginPath = path.join(__dirname, ".claude/plugins/erik-interaction");

console.log("🔍 Validating Erik Interaction Plugin\n");
console.log(`Plugin path: ${pluginPath}\n`);

const errors = [];
const warnings = [];
const success = [];

// 1. Check plugin directory exists
if (!fs.existsSync(pluginPath)) {
  errors.push("Plugin directory not found");
} else {
  success.push("✓ Plugin directory exists");
}

// 2. Check plugin.json
const pluginJsonPath = path.join(pluginPath, "plugin.json");
if (!fs.existsSync(pluginJsonPath)) {
  errors.push("plugin.json not found");
} else {
  try {
    const pluginJson = JSON.parse(fs.readFileSync(pluginJsonPath, "utf8"));
    success.push("✓ plugin.json is valid JSON");

    // Validate required fields
    if (!pluginJson.name) errors.push('plugin.json missing "name" field');
    else success.push(`✓ Plugin name: ${pluginJson.name}`);

    if (!pluginJson.version) warnings.push('plugin.json missing "version" field');
    else success.push(`✓ Plugin version: ${pluginJson.version}`);

    if (!pluginJson.skills || !Array.isArray(pluginJson.skills)) {
      errors.push('plugin.json missing "skills" array');
    } else {
      success.push(`✓ ${pluginJson.skills.length} skills declared`);

      // Check each skill file exists
      pluginJson.skills.forEach((skill) => {
        const skillPath = path.join(pluginPath, "skills", `${skill}.md`);
        if (fs.existsSync(skillPath)) {
          success.push(`  ✓ Skill: ${skill}.md`);
        } else {
          errors.push(`Skill file not found: skills/${skill}.md`);
        }
      });
    }

    // Check hooks
    if (pluginJson.hooks) {
      Object.entries(pluginJson.hooks).forEach(([hookName, hookFiles]) => {
        success.push(`✓ Hook: ${hookName}`);
        hookFiles.forEach((hookFile) => {
          const hookPath = path.join(pluginPath, hookFile);
          if (fs.existsSync(hookPath)) {
            success.push(`  ✓ ${hookFile}`);
            // Check if executable
            try {
              fs.accessSync(hookPath, fs.constants.X_OK);
              success.push(`    ✓ Executable`);
            } catch {
              warnings.push(`    ⚠ ${hookFile} not executable`);
            }
          } else {
            errors.push(`Hook file not found: ${hookFile}`);
          }
        });
      });
    }
  } catch (error) {
    errors.push(`plugin.json parse error: ${error.message}`);
  }
}

// 3. Check directory structure
const requiredDirs = ["skills", "hooks", "scripts"];
requiredDirs.forEach((dir) => {
  const dirPath = path.join(pluginPath, dir);
  if (fs.existsSync(dirPath)) {
    const files = fs.readdirSync(dirPath);
    success.push(`✓ ${dir}/ directory (${files.length} files)`);
  } else {
    warnings.push(`${dir}/ directory not found`);
  }
});

// 4. Check Python scripts
const scripts = ["context-loader.py", "jr-validator.py", "memory-updater.py"];
scripts.forEach((script) => {
  const scriptPath = path.join(pluginPath, "scripts", script);
  if (fs.existsSync(scriptPath)) {
    success.push(`✓ Script: ${script}`);
    // Check if executable
    try {
      fs.accessSync(scriptPath, fs.constants.X_OK);
      success.push(`  ✓ Executable`);
    } catch {
      warnings.push(`  ⚠ ${script} not executable`);
    }
  } else {
    errors.push(`Script not found: scripts/${script}`);
  }
});

// Print results
console.log("=== VALIDATION RESULTS ===\n");

if (success.length > 0) {
  console.log("✅ SUCCESS:\n");
  success.forEach((msg) => console.log(msg));
  console.log("");
}

if (warnings.length > 0) {
  console.log("⚠️  WARNINGS:\n");
  warnings.forEach((msg) => console.log(msg));
  console.log("");
}

if (errors.length > 0) {
  console.log("❌ ERRORS:\n");
  errors.forEach((msg) => console.log(msg));
  console.log("");
  console.log("Plugin validation FAILED");
  process.exit(1);
} else {
  console.log("✅ Plugin structure is VALID\n");
  console.log("NEXT: Run `node load-erik-plugin.mjs` to load the plugin");
  process.exit(0);
}

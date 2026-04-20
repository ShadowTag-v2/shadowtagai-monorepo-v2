#!/usr/bin/env node

/**
 * Output Style Loader Utility
 *
 * Loads and applies output styles for Claude Agent SDK.
 * Output styles customize Claude's system prompt and behavior.
 *
 * Usage:
 *   const { loadOutputStyle } = require('./output-style-loader');
 *   const systemPrompt = await loadOutputStyle('explanatory');
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');

/**
 * Parse YAML frontmatter from a markdown file
 * @param {string} content - The markdown file content
 * @returns {object} - { frontmatter: {...}, content: '...' }
 */
function parseFrontmatter(content) {
  const frontmatterRegex = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/;
  const match = content.match(frontmatterRegex);

  if (!match) {
    return { frontmatter: {}, content };
  }

  const [, frontmatterStr, markdownContent] = match;
  const frontmatter = {};

  // Simple YAML parser for our use case
  frontmatterStr.split('\n').forEach((line) => {
    const colonIndex = line.indexOf(':');
    if (colonIndex > 0) {
      const key = line.substring(0, colonIndex).trim();
      const value = line.substring(colonIndex + 1).trim();
      frontmatter[key] = value;
    }
  });

  return { frontmatter, content: markdownContent };
}

/**
 * Get the path to the output styles directory
 * @param {string} level - 'project' or 'user'
 * @returns {string} - Absolute path to output styles directory
 */
function getOutputStylesPath(level = 'project') {
  if (level === 'user') {
    return path.join(os.homedir(), '.claude', 'output-styles');
  }
  return path.join(process.cwd(), '.claude', 'output-styles');
}

/**
 * Get the path to settings.local.json
 * @returns {string} - Absolute path to settings.local.json
 */
function getSettingsPath() {
  return path.join(process.cwd(), '.claude', 'settings.local.json');
}

/**
 * List all available output styles
 * @returns {Promise<Array>} - Array of { name, description, path, level }
 */
async function listOutputStyles() {
  const styles = [];

  // Check project-level styles
  const projectPath = getOutputStylesPath('project');
  try {
    const files = await fs.readdir(projectPath);
    for (const file of files) {
      if (file.endsWith('.md')) {
        const filePath = path.join(projectPath, file);
        const content = await fs.readFile(filePath, 'utf-8');
        const { frontmatter } = parseFrontmatter(content);
        styles.push({
          name: frontmatter.name || path.basename(file, '.md'),
          description: frontmatter.description || 'No description',
          path: filePath,
          level: 'project',
          filename: file,
        });
      }
    }
  } catch (err) {
    // Directory doesn't exist or can't be read
  }

  // Check user-level styles
  const userPath = getOutputStylesPath('user');
  try {
    const files = await fs.readdir(userPath);
    for (const file of files) {
      if (file.endsWith('.md')) {
        const filePath = path.join(userPath, file);
        const content = await fs.readFile(filePath, 'utf-8');
        const { frontmatter } = parseFrontmatter(content);
        styles.push({
          name: frontmatter.name || path.basename(file, '.md'),
          description: frontmatter.description || 'No description',
          path: filePath,
          level: 'user',
          filename: file,
        });
      }
    }
  } catch (err) {
    // Directory doesn't exist or can't be read
  }

  return styles;
}

/**
 * Find an output style by name
 * @param {string} styleName - Name of the style to find
 * @returns {Promise<object|null>} - Style object or null if not found
 */
async function findOutputStyle(styleName) {
  const styles = await listOutputStyles();
  const normalizedName = styleName.toLowerCase();

  // First try exact match
  let style = styles.find((s) => s.name.toLowerCase() === normalizedName);
  if (style) return style;

  // Try filename match
  style = styles.find((s) => path.basename(s.filename, '.md').toLowerCase() === normalizedName);

  return style || null;
}

/**
 * Load an output style and return its content
 * @param {string} styleName - Name of the style to load
 * @returns {Promise<string>} - The system prompt content
 */
async function loadOutputStyle(styleName) {
  const style = await findOutputStyle(styleName);

  if (!style) {
    throw new Error(`Output style '${styleName}' not found`);
  }

  const content = await fs.readFile(style.path, 'utf-8');
  const { content: systemPrompt } = parseFrontmatter(content);

  return systemPrompt.trim();
}

/**
 * Get the currently active output style from settings
 * @returns {Promise<string|null>} - Name of active style or null
 */
async function getActiveOutputStyle() {
  try {
    const settingsPath = getSettingsPath();
    const content = await fs.readFile(settingsPath, 'utf-8');
    const settings = JSON.parse(content);
    return settings.outputStyle || null;
  } catch (err) {
    return null;
  }
}

/**
 * Set the active output style in settings
 * @param {string} styleName - Name of the style to activate
 * @returns {Promise<void>}
 */
async function setActiveOutputStyle(styleName) {
  // Verify the style exists
  const style = await findOutputStyle(styleName);
  if (!style) {
    throw new Error(`Output style '${styleName}' not found`);
  }

  const settingsPath = getSettingsPath();
  let settings = {};

  // Read existing settings if they exist
  try {
    const content = await fs.readFile(settingsPath, 'utf-8');
    settings = JSON.parse(content);
  } catch (err) {
    // File doesn't exist or is invalid, start fresh
  }

  // Update the outputStyle field
  settings.outputStyle = styleName;

  // Ensure directory exists
  await fs.mkdir(path.dirname(settingsPath), { recursive: true });

  // Write back to file
  await fs.writeFile(settingsPath, JSON.stringify(settings, null, 2) + '\n', 'utf-8');
}

/**
 * Load the currently active output style, or fall back to default
 * @returns {Promise<string>} - The system prompt content
 */
async function loadActiveOutputStyle() {
  const activeStyle = await getActiveOutputStyle();

  if (activeStyle) {
    try {
      return await loadOutputStyle(activeStyle);
    } catch (err) {
      console.warn(
        `Warning: Could not load active style '${activeStyle}', falling back to default`,
      );
    }
  }

  // Fall back to default style if available
  try {
    return await loadOutputStyle('default');
  } catch (err) {
    // No default style available, return empty string
    return '';
  }
}

// CLI interface
if (require.main === module) {
  const command = process.argv[2];
  const arg = process.argv[3];

  (async () => {
    try {
      switch (command) {
        case 'list': {
          const styles = await listOutputStyles();
          console.log('\nAvailable Output Styles:\n');

          const projectStyles = styles.filter((s) => s.level === 'project');
          if (projectStyles.length > 0) {
            console.log('Project Styles (.claude/output-styles/):');
            projectStyles.forEach((s) => {
              console.log(`  • ${s.name} - ${s.description}`);
            });
            console.log();
          }

          const userStyles = styles.filter((s) => s.level === 'user');
          if (userStyles.length > 0) {
            console.log('User Styles (~/.claude/output-styles/):');
            userStyles.forEach((s) => {
              console.log(`  • ${s.name} - ${s.description}`);
            });
            console.log();
          }

          const active = await getActiveOutputStyle();
          if (active) {
            console.log(`Active: ${active}\n`);
          }
          break;
        }

        case 'get': {
          if (!arg) {
            console.error('Usage: output-style-loader.js get <style-name>');
            process.exit(1);
          }
          const content = await loadOutputStyle(arg);
          console.log(content);
          break;
        }

        case 'set':
          if (!arg) {
            console.error('Usage: output-style-loader.js set <style-name>');
            process.exit(1);
          }
          await setActiveOutputStyle(arg);
          console.log(`✓ Activated output style: ${arg}`);
          break;

        case 'active': {
          const activeContent = await loadActiveOutputStyle();
          console.log(activeContent);
          break;
        }

        default:
          console.log(`
Output Style Loader - Manage Claude output styles

Usage:
  node output-style-loader.js list              List all available styles
  node output-style-loader.js get <name>        Get content of a specific style
  node output-style-loader.js set <name>        Set active style for this project
  node output-style-loader.js active            Get content of active style

Examples:
  node output-style-loader.js list
  node output-style-loader.js set explanatory
  node output-style-loader.js get learning
          `);
      }
    } catch (err) {
      console.error('Error:', err.message);
      process.exit(1);
    }
  })();
}

module.exports = {
  loadOutputStyle,
  listOutputStyles,
  findOutputStyle,
  getActiveOutputStyle,
  setActiveOutputStyle,
  loadActiveOutputStyle,
  parseFrontmatter,
};

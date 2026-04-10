# Gemini CLI Configuration

Gemini CLI offers several ways to configure its behavior, including environment variables, command-line arguments, and settings files. This document outlines the different configuration methods and available settings.

## Configuration layers

Configuration is applied in the following order of precedence (lower numbers are overridden by higher numbers):

1. **Default values:** Hardcoded defaults within the application.
2. **User settings file:** Global settings for the current user.
3. **Project settings file:** Project-specific settings.
4. **System settings file:** System-wide settings.
5. **Environment variables:** System-wide or session-specific variables, potentially loaded from `.env` files.
6. **Command-line arguments:** Values passed when launching the CLI.

## Settings files

Gemini CLI uses `settings.json` files for persistent configuration. There are three locations for these files:

- **User settings file:**
  - **Location:** `~/.gemini/settings.json` (where `~` is your home directory).
  - **Scope:** Applies to all Gemini CLI sessions for the current user.
- **Project settings file:**
  - **Location:** `.gemini/settings.json` within your project's root directory.
  - **Scope:** Applies only when running Gemini CLI from that specific project. Project settings override user settings.
- **System settings file:**
  - **Location:** `/etc/gemini-cli/settings.json` (Linux), `C:\ProgramData\gemini-cli\settings.json` (Windows) or `/Library/Application Support/GeminiCli/settings.json` (macOS). The path can be overridden using the `GEMINI_CLI_SYSTEM_SETTINGS_PATH` environment variable.
  - **Scope:** Applies to all Gemini CLI sessions on the system, for all users. System settings override user and project settings.

**Note on environment variables in settings:** String values within your `settings.json` files can reference environment variables using either `$VAR_NAME` or `${VAR_NAME}` syntax.

### The `.gemini` directory in your project

In addition to a project settings file, a project's `.gemini` directory can contain other project-specific files related to Gemini CLI's operation, such as:

- Custom sandbox profiles (e.g., `.gemini/sandbox-macos-custom.sb`, `.gemini/sandbox.Dockerfile`).

### Available settings in `settings.json`

- **`contextFileName`** (string or array of strings): Specifies the filename for context files (e.g., `GEMINI.md`, `AGENTS.md`). Default: `GEMINI.md`.
- **`bugCommand`** (object): Overrides the default URL for the `/bug` command.
- **`fileFiltering`** (object): Controls git-aware file filtering (`respectGitIgnore`, `enableRecursiveFileSearch`).
- **`coreTools`** (array of strings): Specifies a list of core tool names to be made available.
- **`excludeTools`** (array of strings): Specifies a list of core tool names to be excluded.
- **`allowMCPServers`** (array of strings): Whitelist of MCP server names.
- **`excludeMCPServers`** (array of strings): Blacklist of MCP server names.
- **`autoAccept`** (boolean): Controls whether the CLI automatically accepts safe tool calls. Default: `false`.
- **`theme`** (string): Sets the visual theme. Default: `"Default"`.
- **`vimMode`** (boolean): Enables vim mode for input editing. Default: `false`.
- **`sandbox`** (boolean or string): Controls sandboxing. Default: `false`.
- **`toolDiscoveryCommand`** (string): Custom shell command for discovering tools.
- **`toolCallCommand`** (string): Custom shell command for calling a specific tool.
- **`mcpServers`** (object): Configures connections to MCP servers.
- **`checkpointing`** (object): Configures checkpointing (`enabled`).
- **`preferredEditor`** (string): Specifies the preferred editor for diffs. Default: `vscode`.
- **`telemetry`** (object): Configures logging and metrics collection.
- **`usageStatisticsEnabled`** (boolean): Enables/disables usage statistics. Default: `true`.
- **`hideTips`** (boolean): Enables/disables helpful tips. Default: `false`.
- **`hideBanner`** (boolean): Enables/disables the startup banner. Default: `false`.
- **`maxSessionTurns`** (number): Sets the maximum number of turns for a session. Default: `-1` (unlimited).
- **`summarizeToolOutput`** (object): Enables/disables summarization of tool output.
- **`excludedProjectEnvVars`** (array of strings): Specifies environment variables excluded from project `.env` files.
- **`includeDirectories`** (array of strings): Additional directories to include in the workspace.
- **`loadMemoryFromIncludeDirectories`** (boolean): Controls loading `GEMINI.md` from included directories.

## Shell History

The CLI keeps a history of shell commands you run in `~/.gemini/tmp/<project_hash>/shell_history`.

## Environment Variables & `.env` Files

The CLI automatically loads environment variables from an `.env` file.

- **`GEMINI_API_KEY`** (Required): Your API key for the Gemini API.
- **`GEMINI_MODEL`**: Default Gemini model.
- **`GEMINI_CLI_CUSTOM_HEADERS`**: Extra HTTP headers.
- **`GEMINI_API_KEY_AUTH_MECHANISM`**: Auth mechanism (`x-goog-api-key` or `bearer`).
- **`GOOGLE_API_KEY`**: Google Cloud API key.
- **`GOOGLE_CLOUD_PROJECT`**: Google Cloud Project ID.
- **`GOOGLE_APPLICATION_CREDENTIALS`**: Path to Google Application Credentials JSON file.
- **`GEMINI_SANDBOX`**: Alternative to `sandbox` setting.
- **`HTTP_PROXY` / `HTTPS_PROXY`**: Proxy server.
- **`SEATBELT_PROFILE`**: macOS sandbox profile.
- **`DEBUG` / `DEBUG_MODE`**: Enable verbose debug logging.
- **`NO_COLOR`**: Disable color output.
- **`CLI_TITLE`**: Customize CLI title.
- **`CODE_ASSIST_ENDPOINT`**: Code assist server endpoint.
- **`GEMINI_SYSTEM_MD`**: Override base system prompt with a file.
- **`GEMINI_WRITE_SYSTEM_MD`**: Write default system prompt to a file.

## Command-Line Arguments

- **`--model`** (**`-m`**): Specifies the Gemini model.
- **`--prompt`** (**`-p`**): Pass a prompt directly (non-interactive).
- **`--prompt-interactive`** (**`-i`**): Start interactive session with prompt.
- **`--sandbox`** (**`-s`**): Enable sandbox mode.
- **`--sandbox-image`**: Set sandbox image URI.
- **`--debug`** (**`-d`**): Enable debug mode.
- **`--all-files`** (**`-a`**): Include all files as context.
- **`--help`** (**`-h`**): Display help.
- **`--show-memory-usage`**: Display memory usage.
- **`--yolo`**: Automatically approve all tool calls.
- **`--telemetry`**: Enable telemetry.
- **`--extensions`** (**`-e`**): Specify extensions.
- **`--list-extensions`** (**`-l`**): List extensions.
- **`--include-directories`**: Include additional directories.
- **`--version`**: Display version.

## Context Files (Hierarchical Instructional Context)

Context files (default `GEMINI.md`) configure the instructional context ("memory").

- **Purpose:** Instructions, guidelines, context.
- **Hierarchy:**
  1. **Global Context File:** `~/.gemini/GEMINI.md`
  2. **Project Root & Ancestors Context Files**
  3. **Sub-directory Context Files**
- **Commands:**
  - `/memory refresh`: Re-scan and reload context files.
  - `/memory show`: Display combined instructional context.

## Sandboxing

Sandboxing is disabled by default. Enable using `--sandbox`, `GEMINI_SANDBOX`, or `settings.json`.
By default, uses `gemini-cli-sandbox` Docker image.
Custom Dockerfile: `.gemini/sandbox.Dockerfile`.

## Usage Statistics

The CLI collects anonymized usage statistics (tool calls, API requests, session info) to improve the tool.
It does **NOT** collect PII, prompt/response content, or file content.
Opt out by setting `"usageStatisticsEnabled": false` in `settings.json`.

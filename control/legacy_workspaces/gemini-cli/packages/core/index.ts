/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

export { getCodeAssistServer } from "./src/code_assist/codeAssist.js";
export { getExperiments } from "./src/code_assist/experiments/experiments.js";
export {
  DEFAULT_TRUNCATE_TOOL_OUTPUT_LINES,
  DEFAULT_TRUNCATE_TOOL_OUTPUT_THRESHOLD,
} from "./src/config/config.js";
export {
  DEFAULT_GEMINI_EMBEDDING_MODEL,
  DEFAULT_GEMINI_FLASH_LITE_MODEL,
  DEFAULT_GEMINI_FLASH_MODEL,
  DEFAULT_GEMINI_MODEL,
  DEFAULT_GEMINI_MODEL_AUTO,
  GEMINI_MODEL_ALIAS_FLASH,
  GEMINI_MODEL_ALIAS_FLASH_LITE,
  GEMINI_MODEL_ALIAS_PRO,
} from "./src/config/models.js";
export { Storage } from "./src/config/storage.js";
export { detectIdeFromEnv } from "./src/ide/detect-ide.js";
export * from "./src/index.js";
export { KeychainTokenStorage } from "./src/mcp/token-storage/keychain-token-storage.js";
export { ClearcutLogger } from "./src/telemetry/clearcut-logger/clearcut-logger.js";
export {
  logExtensionDisable,
  logExtensionEnable,
  logIdeConnection,
  logModelSlashCommand,
} from "./src/telemetry/loggers.js";
export {
  ExtensionDisableEvent,
  ExtensionEnableEvent,
  ExtensionInstallEvent,
  ExtensionUninstallEvent,
  ExtensionUpdateEvent,
  IdeConnectionEvent,
  IdeConnectionType,
  ModelSlashCommandEvent,
} from "./src/telemetry/types.js";
export { makeFakeConfig } from "./src/test-utils/config.js";
export type { GoogleApiError } from "./src/utils/googleErrors.js";
export * from "./src/utils/googleQuotaErrors.js";
export { getErrorStatus, ModelNotFoundError } from "./src/utils/httpErrors.js";
export * from "./src/utils/pathReader.js";
export {
  type AnsiLine,
  type AnsiOutput,
  type AnsiToken,
  serializeTerminalToObject,
} from "./src/utils/terminalSerializer.js";

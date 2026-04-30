// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

export { DesignSystem } from '../generated/src/designsystem.js';
export { Project } from '../generated/src/project.js';
export { Screen } from '../generated/src/screen.js';
// Domain classes (generated)
export { Stitch } from '../generated/src/stitch.js';
// Tool catalog (generated)
export {
  type ToolDefinition,
  type ToolInputSchema,
  type ToolPropertySchema,
  toolDefinitions,
} from '../generated/src/tool-definitions.js';
// Infrastructure (handwritten)
export { StitchToolClient } from './client.js';
// FIFE URL utilities
export { buildFifeSuffix, type FifeImageOptions } from './fife.js';
export { StitchProxy } from './proxy/core.js';
// Singleton
export { stitch } from './singleton.js';
// Types (config + data interfaces)
export type { StitchConfig, StitchConfigInput } from './spec/client.js';
// Error handling
export { StitchError, StitchErrorCode } from './spec/errors.js';
export { StitchProxyConfigSchema } from './spec/proxy.js';
export { type ToolInfo, type ToolParam, toolMap } from './tool-map.js';
export type {
  DesignTheme,
  GenerateScreenParams,
  ProjectData,
  ScreenInstance,
  ThumbnailScreenshot,
} from './types.js';

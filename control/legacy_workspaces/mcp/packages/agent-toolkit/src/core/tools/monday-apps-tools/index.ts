import { appTools } from "./app";
import { appFeatureTools } from "./app-feature";
import { appVersionTools } from "./app-version";
import type { MondayAppsToolType } from "./base-tool/base-monday-apps-tool";
import { MondayAppsToolCategory } from "./consts/apps.consts";
import { codeTools } from "./monday-code";
import { storageTools } from "./storage";

export const mondayAppsTools = {
  [MondayAppsToolCategory.STORAGE]: storageTools,
  [MondayAppsToolCategory.APP]: appTools,
  [MondayAppsToolCategory.APP_VERSION]: appVersionTools,
  [MondayAppsToolCategory.APP_FEATURE]: appFeatureTools,
  [MondayAppsToolCategory.MONDAY_CODE]: codeTools,
};

export const allMondayAppsTools: MondayAppsToolType[] = [
  ...storageTools,
  ...appTools,
  ...appVersionTools,
  ...appFeatureTools,
  ...codeTools,
];

export * from "./app";
export * from "./app-feature";
export * from "./app-version";
export * from "./monday-code";
export * from "./storage";

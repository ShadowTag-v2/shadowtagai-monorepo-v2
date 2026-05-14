// @ts-check
import * as path from "node:path";
import type { ParserOptions } from "prettier";
import prettier from "prettier";
import * as console from "./console";
import { expiringMap } from "./expiring-map.js";
import { getTailwindConfig as getTailwindConfigFromLib } from "./sorter.js";
import type { UnifiedApi } from "./types";
import { cacheForDirs } from "./utils.js";

const prettierConfigCache = expiringMap<string, string | null>(10_000);

async function resolvePrettierConfigDir(filePath: string, inputDir: string): Promise<string> {
  // Check cache for this directory
  const cached = prettierConfigCache.get(inputDir);
  if (cached !== undefined) {
    return cached ?? process.cwd();
  }

  const resolve = async () => {
    try {
      return await prettier.resolveConfigFile(filePath);
    } catch (err) {
      console.error("prettier-config-not-found", "Failed to resolve Prettier Config");
      console.error("prettier-config-not-found-err", err);
      return null;
    }
  };

  const prettierConfig = await resolve();

  // Cache all directories from inputDir up to config location
  if (prettierConfig) {
    const configDir = path.dirname(prettierConfig);
    cacheForDirs(prettierConfigCache, inputDir, configDir, configDir);
    return configDir;
  } else {
    prettierConfigCache.set(inputDir, null);
    return process.cwd();
  }
}

export async function getTailwindConfig(options: ParserOptions): Promise<UnifiedApi> {
  const cwd = process.cwd();
  const inputDir = options.filepath ? path.dirname(options.filepath) : cwd;

  // Only resolve prettier config dir if we need it for relative path resolution
  const needsPrettierConfig =
    (options.tailwindConfig && !path.isAbsolute(options.tailwindConfig)) ||
    (options.tailwindStylesheet && !path.isAbsolute(options.tailwindStylesheet)) ||
    (options.tailwindEntryPoint && !path.isAbsolute(options.tailwindEntryPoint));

  let configDir: string;
  if (needsPrettierConfig) {
    configDir = await resolvePrettierConfigDir(options.filepath, inputDir);
  } else {
    configDir = cwd;
  }

  const configPath =
    options.tailwindConfig && !options.tailwindConfig.endsWith(".css")
      ? options.tailwindConfig
      : undefined;

  let stylesheetPath = options.tailwindStylesheet;
  if (!stylesheetPath && options.tailwindEntryPoint) {
    console.warn(
      "entrypoint-is-deprecated",
      configDir,
      "Deprecated: Use the `tailwindStylesheet` option for v4 projects instead of `tailwindEntryPoint`.",
    );
    stylesheetPath = options.tailwindEntryPoint;
  }

  if (!stylesheetPath && options.tailwindConfig && options.tailwindConfig.endsWith(".css")) {
    console.warn(
      "config-as-css-is-deprecated",
      configDir,
      "Deprecated: Use the `tailwindStylesheet` option for v4 projects instead of `tailwindConfig`.",
    );
    stylesheetPath = options.tailwindConfig;
  }

  return getTailwindConfigFromLib({
    base: configDir,
    filepath: options.filepath,
    configPath,
    stylesheetPath,
    packageName: options.tailwindPackageName,
  });
}

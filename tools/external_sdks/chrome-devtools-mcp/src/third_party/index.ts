/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import "core-js/modules/es.promise.with-resolvers.js";
import "core-js/modules/es.set.union.v2.js";
import "core-js/proposals/iterator-helpers.js";

import type { Flags, OutputMode, Result, RunnerResult } from "lighthouse";
import type { Page } from "puppeteer-core";

export type { Flags, Result, RunnerResult, OutputMode };

export { Client } from "@modelcontextprotocol/sdk/client/index.js";
export { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
export { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
export { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
export {
	type CallToolResult,
	type ImageContent,
	SetLevelRequestSchema,
	type TextContent,
} from "@modelcontextprotocol/sdk/types.js";
export {
	Browser as BrowserEnum,
	type ChromeReleaseChannel as BrowsersChromeReleaseChannel,
	detectBrowserPlatform,
	resolveDefaultUserDataDir,
} from "@puppeteer/browsers";
export type { Debugger } from "debug";
export { default as debug } from "debug";
export type * from "puppeteer-core";
export {
	CDPSessionEvent,
	default as puppeteer,
	KnownDevices,
	Locator,
	PredefinedNetworkConditions,
} from "puppeteer-core";
export type { CdpPage } from "puppeteer-core/internal/cdp/Page.js";
export { PipeTransport } from "puppeteer-core/internal/node/PipeTransport.js";
export type { Options as YargsOptions } from "yargs";
export { default as yargs } from "yargs";
export { hideBin } from "yargs/helpers";
export { z as zod } from "zod";

import {
	generateReport as generateReportImpl,
	navigation as navigationImpl,
	snapshot as snapshotImpl,
} from "./lighthouse-devtools-mcp-bundle.js";

export const snapshot = snapshotImpl as (
	page: Page,
	options: { flags?: Flags },
) => Promise<RunnerResult>;
export const navigation = navigationImpl as (
	page: Page,
	url: string,
	options: { flags?: Flags },
) => Promise<RunnerResult>;
export const generateReport = generateReportImpl as (
	lhr: Result,
	format: string,
) => string;

export * as DevTools from "../../node_modules/chrome-devtools-frontend/mcp/mcp.js";

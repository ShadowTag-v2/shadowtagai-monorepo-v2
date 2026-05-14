#!/usr/bin/env node
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { ToolMode } from "@mondaydotcomorg/agent-toolkit/core";
import { MondayAgentToolkit } from "@mondaydotcomorg/agent-toolkit/mcp";
import dotenv from "dotenv";
import { runAtpMcpServer } from "./domains/atp/index.js";
import { parseArgs, validateArgs } from "./utils/args/args.service.js";

dotenv.config();

async function runMcpServer(validatedArgs: ReturnType<typeof validateArgs>): Promise<void> {
  const toolkit = new MondayAgentToolkit({
    mondayApiToken: validatedArgs.token,
    mondayApiVersion: validatedArgs.version,
    mondayApiRequestConfig: {},
    toolsConfiguration: {
      readOnlyMode: validatedArgs.readOnlyMode,
      enableDynamicApiTools: validatedArgs.enableDynamicApiTools,
      mode: validatedArgs.mode,
      enableToolManager: false,
    },
  });

  const transport = new StdioServerTransport();
  await toolkit.connect(transport);
}

async function runServer(): Promise<void> {
  const args = process.argv.slice(2);
  const parsedArgs = parseArgs(args);
  const validatedArgs = validateArgs(parsedArgs);

  if (validatedArgs.mode === ToolMode.ATP) {
    await runAtpMcpServer({
      token: validatedArgs.token,
      version: validatedArgs.version,
    });
  } else {
    await runMcpServer(validatedArgs);
  }
}

runServer().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});

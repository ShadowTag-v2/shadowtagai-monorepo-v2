import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
  RemoteAdapter,
} from '@copilotkit/runtime'; // Check import path if needed, usually exported from main
import type { NextRequest } from 'next/server';

// ADK / AG-UI Bridge
// This route acts as the gateway between the React Frontend and the ADK Agent (Flying n-autoresearch/Kosmos/BioAgents)

const serviceAdapter = new RemoteAdapter({
  url: 'http://127.0.0.1:8080',
});

// Actually, effectively, if the python backend IS the runtime, we might just need to point the frontend to it.
// BUT, to avoid CORS issues and add flexibility, a Next.js Proxy is good.
// Let's use the CopilotRuntime with a RemoteAction.

// FOR NOW: We will implement a simple Proxy logic or use the runtime to forward.
// Simplest Path: The Frontend <CopilotKit> url points DIRECTLY to the Python Backend
// if the Python Backend implements the CopilotKit Protocol (which ag_ui_adk does).
// So this route.ts might be optional if we point directly.
// HOWEVER, typically we want a route for the "Runtime" to live.
// If using ag_ui_adk, the Python backend IS the runtime.
// So we just need to point the frontend `runtimeUrl` to `http://localhost:8000`.
// So this file might NOT be needed if we point directly.
// BUT, let's keep it standard.
// If we want to use the Next.js app as the *host* of the runtime, we'd import the agent here.
// But our agent is Python.
// So, the Python backend acts as the "Standard CopilotKit Endpoint".
// Thus, we don't strictly *need* this route.ts if we point the Provider to localhost:8000.
// BUT, to avoid CORS (port 3000 vs 8000), a proxy is nice.
// Let's CREATE it effectively as a proxy or just skip it and configure the Provider.
// I will create it as a standard simple runtime just in case we need to add local JS actions later.
// It will serve as a local runtime that *could* have other tools.
// But for the ADK agent, we connect via "Remote Endpoint".

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime: new CopilotRuntime(),
    serviceAdapter,
    endpoint: '/api/copilotkit',
  });

  return handleRequest(req);
};

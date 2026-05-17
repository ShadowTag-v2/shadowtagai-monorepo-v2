import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
  ExperimentalEmptyAdapter,
} from "@copilotkit/runtime";
import { HttpAgent } from "@copilotkit/runtime-client-gql"; // Adapting imports based on standard CopilotKit usage
import type { NextRequest } from "next/server";

// We assume the Wing Commander Agent is running on Cloud Run
const WING_COMMANDER_URL =
  process.env.WING_COMMANDER_URL || "https://wing-commander-func-s2its66sea-uc.a.run.app";

const runtime = new CopilotRuntime({
  agents: {
    wing_commander: {
      name: "wing_commander",
      description: "The God Mode Agent Swarm",
      url: WING_COMMANDER_URL,
    },
  },
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter: new ExperimentalEmptyAdapter(),
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};

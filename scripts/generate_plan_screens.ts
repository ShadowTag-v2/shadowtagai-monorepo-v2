/**
 * V23 Task 6: Generate Stitch MCP plan visualization screens
 * Uses the StitchMCP tool interface for screen generation.
 */

import { $ } from "bun";

export async function generateMcpScreens(planTitle: string = "KAIROS Architectural Plan") {
  console.log(`⚡ [StitchMCP] Generating visual plan representations for: ${planTitle}`);

  try {
    const result = await $`bunx --bun mcp-cli call StitchMCP generate_screen "${planTitle}"`.text();
    console.log(`✅ [StitchMCP] Screen generated: ${result.substring(0, 200)}`);
    return result;
  } catch {
    console.log("⚠️ [StitchMCP] Server offline — screen generation deferred to next heartbeat.");
    return null;
  }
}

if (import.meta.main) {
  await generateMcpScreens(process.argv[2] || "KAIROS V23 Dashboard");
}

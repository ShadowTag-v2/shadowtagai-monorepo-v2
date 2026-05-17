import { feature } from "bun:bundle";
import { logEvent } from "../../services/analytics/index.js";
import { isEnvTruthy } from "../../utils/envUtils.js";

export function isKairosMode(): boolean {
  if (feature("KAIROS_MODE")) {
    return isEnvTruthy(process.env.CLAUDE_CODE_KAIROS_MODE);
  }
  return false;
}

export function matchSessionMode(sessionMode: "kairos" | "normal" | undefined): string | undefined {
  if (!sessionMode) return undefined;

  const currentIsKairos = isKairosMode();
  const sessionIsKairos = sessionMode === "kairos";

  if (currentIsKairos === sessionIsKairos) return undefined;

  if (sessionIsKairos) {
    process.env.CLAUDE_CODE_KAIROS_MODE = "1";
  } else {
    delete process.env.CLAUDE_CODE_KAIROS_MODE;
  }

  logEvent("tengu_kairos_mode_switched", { to: sessionMode as any });

  return sessionIsKairos ? "Entered KAIROS proactive mode." : "Exited KAIROS proactive mode.";
}

export function getKairosSystemPrompt(): string {
  return `You are KAIROS, a background autonomous agent operating proactively.
Your job is to identify opportunities, research them, and stage improvements for the user without being prompted.
You will run in the background, utilizing idle cycles to maintain repo health, update KIs, and audit performance.
When interacting with the user, provide concise summaries of your background actions.
Do not require explicit user input to proceed if confidence is high.`;
}

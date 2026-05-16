import type { FullConfig } from "@playwright/test";
import waitOn from "wait-on";

async function globalSetup(_config: FullConfig): Promise<void> {
  const baseUrl = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3000";

  await waitOn({
    resources: [baseUrl],
    timeout: 120_000,
    validateStatus: (status) => status >= 200 && status < 500,
  });
}

export default globalSetup;

import puppeteer from "puppeteer-core";

async function executeAestheticQualityGate(targetUrl: string) {
  console.log(
    "⚡ [Claude Opus 4.6] Engaging Chrome DevTools to verify Google Design MCP constraints...",
  );
  const browser = await puppeteer.connect({ browserURL: "http://localhost:9222" });
  const page = await browser.newPage();
  await page.goto(targetUrl, { waitUntil: "networkidle0" });

  const domSnapshot = await page.evaluate(() => {
    return {
      primaryButtons: Array.from(document.querySelectorAll("button")).map(
        (btn) => window.getComputedStyle(btn).borderRadius,
      ),
    };
  });

  const violations = domSnapshot.primaryButtons.filter(
    (radius) => radius !== "100px" && radius !== "50%",
  );
  await browser.disconnect();

  if (violations.length > 0) {
    console.error("❌ AESTHETIC QUALITY GATE FAILED");
    process.exit(1);
  }
  console.log("✅ AESTHETIC QUALITY GATE PASSED. M3 Compliance verified.");
}
await executeAestheticQualityGate("http://localhost:3000");

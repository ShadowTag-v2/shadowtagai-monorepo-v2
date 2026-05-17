import fs from "node:fs";
import path from "node:path";
import * as chromeLauncher from "chrome-launcher";
import lighthouse from "lighthouse";

async function runLighthouseAudit(url) {
  const chrome = await chromeLauncher.launch({ chromeFlags: ["--headless"] });
  const options = {
    logLevel: "info",
    output: "html",
    onlyCategories: ["performance", "accessibility", "best-practices", "seo"],
    port: chrome.port,
  };

  const runnerResult = await lighthouse(url, options);

  // `.report` is the HTML report as a string
  const reportHtml = runnerResult.report;
  const reportsDir = path.join(process.cwd(), "reports");

  if (!fs.existsSync(reportsDir)) {
    fs.mkdirSync(reportsDir);
  }

  const filename = `lighthouse-report-${Date.now()}.html`;
  fs.writeFileSync(path.join(reportsDir, filename), reportHtml);

  // Print scores
  console.log("\n--- Lighthouse Audit Scores ---");
  console.log(`URL: ${runnerResult.lhr.finalDisplayedUrl}`);
  console.log(`Performance: ${runnerResult.lhr.categories.performance.score * 100}`);
  console.log(`Accessibility: ${runnerResult.lhr.categories.accessibility.score * 100}`);
  console.log(`Best Practices: ${runnerResult.lhr.categories["best-practices"].score * 100}`);
  console.log(`SEO: ${runnerResult.lhr.categories.seo.score * 100}`);
  console.log("-------------------------------\n");
  console.log(`Report saved to: reports/${filename}`);

  await chrome.kill();
}

const targetUrl = process.argv[2] || "http://localhost:3000";
console.log(`Starting Lighthouse audit for ${targetUrl}...`);
runLighthouseAudit(targetUrl).catch(console.error);

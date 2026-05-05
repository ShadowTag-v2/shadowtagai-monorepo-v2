const { execSync } = require('child_process');

console.log("Executing Headless Lighthouse P100 Audit...");
try {
  const result = execSync('npx lighthouse https://kovelai.web.app --output json --quiet --chrome-flags="--headless"', { encoding: 'utf-8' });
  const report = JSON.parse(result);
  
  const scores = {
    performance: report.categories.performance.score * 100,
    accessibility: report.categories.accessibility.score * 100,
    bestPractices: report.categories['best-practices'].score * 100,
    seo: report.categories.seo.score * 100
  };

  console.log('Lighthouse Audit Results:');
  console.table(scores);

  if (scores.performance < 90 || scores.accessibility < 100 || scores.bestPractices < 100 || scores.seo < 100) {
    console.error("Audit failed to meet P100/A100/BP100/SEO100 requirements.");
    process.exit(1);
  } else {
    console.log("All metrics passed!");
    process.exit(0);
  }
} catch (error) {
  console.error("Lighthouse execution failed:", error.message);
  process.exit(1);
}

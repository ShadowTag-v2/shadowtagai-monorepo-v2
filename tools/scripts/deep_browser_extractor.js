const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(process.argv[2] || 'https://news.ycombinator.com');
  const text = await page.evaluate(() => document.body.innerText);
  console.log(text.slice(0, 2000));
  await browser.close();
})();

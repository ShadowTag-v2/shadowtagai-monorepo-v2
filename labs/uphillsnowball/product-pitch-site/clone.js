import scrape from 'website-scraper';
import PuppeteerPlugin from 'website-scraper-puppeteer';

console.log('[clone] Starting 1:1 structural extraction of unusualmachines.com...');
console.log(
  '[clone] This drives headless Chromium to render all JS tabs/animations before capture.',
);

try {
  await scrape({
    urls: ['https://www.unusualmachines.com/'],
    directory: './clone-base',
    sources: [
      { selector: 'img', attr: 'src' },
      { selector: 'img', attr: 'srcset' },
      { selector: 'link[rel="stylesheet"]', attr: 'href' },
      { selector: 'script', attr: 'src' },
      { selector: 'video source', attr: 'src' },
      { selector: 'video', attr: 'poster' },
      { selector: 'link[rel*="icon"]', attr: 'href' },
      { selector: 'source', attr: 'srcset' },
    ],
    plugins: [
      new PuppeteerPlugin({
        launchOptions: {
          headless: 'new',
          args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
          ],
        },
        scrollToBottom: {
          timeout: 15000,
          viewportN: 10,
        },
        blockNavigation: true,
      }),
    ],
  });
  console.log('[clone] ✅ 1:1 Structural Clone Complete — saved to ./clone-base/');
} catch (err) {
  console.error('[clone] ❌ Extraction failed:', err.message);
  process.exit(1);
}

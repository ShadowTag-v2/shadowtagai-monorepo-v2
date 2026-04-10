const scraper = require("scrape-tiktok");

async function scrapeURL(url) {
  try {
    // Most tiktok scrapers expect a full URL
    const data = await scraper.tiktokScraper(url);
    // We write out minified JSON strictly to stdout so Python can subprocess.check_output it
    console.log(JSON.stringify(data));
  } catch (e) {
    console.error(JSON.stringify({ error: e.message }));
    process.exit(1);
  }
}

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error(JSON.stringify({ error: "No URL provided" }));
  process.exit(1);
}

scrapeURL(args[0]);

const fs = require('fs');
const files = process.argv.slice(2);
for (const f of files) {
  try {
    JSON.parse(fs.readFileSync(f, 'utf8'));
    console.log(`OK ${f}`);
  } catch (e) {
    console.error(`BAD ${f}: ${e.message}`);
    process.exitCode = 1;
  }
}

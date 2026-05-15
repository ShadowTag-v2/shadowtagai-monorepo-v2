# Claude Web Conversation Extractor

Extract conversation data from Claude.ai or code.claude.com for analysis, backup, or migration purposes.

## Methods

### Method 1: Browser Console (Simplest, No Dependencies)

1. **Navigate** to https://claude.ai or https://code.claude.com
2. **Log in** to your account
3. **Open Developer Tools**:
   - Press `F12` (Windows/Linux)
   - Press `Cmd+Option+I` (macOS)
4. **Go to the Console tab**
5. **Paste and run** the extraction script:
   ```bash
   # Copy the script to clipboard
   cat scripts/extract_claude_web.js | pbcopy  # macOS
   cat scripts/extract_claude_web.js | xclip -selection clipboard  # Linux

   # Or just copy the contents of scripts/extract_claude_web.js
   ```
6. **Press Enter** - A JSON file will be downloaded automatically

### Method 2: Automated with Puppeteer (Requires Setup)

For repeated extractions or automation, use the Node.js runner.

#### Setup

1. **Install dependencies** (local machine, not in restricted environments):
   ```bash
   npm install puppeteer
   ```

2. **Run the extractor**:
   ```bash
   # Default (opens browser, extracts from claude.ai)
   node scripts/run_extraction.js

   # Extract from Claude Code Web
   node scripts/run_extraction.js --url https://code.claude.com

   # Run in headless mode (no visible browser)
   node scripts/run_extraction.js --headless

   # Custom output directory
   node scripts/run_extraction.js --output ./my-extractions

   # Full options
   node scripts/run_extraction.js \
     --url https://code.claude.com \
     --headless \
     --output ./backups \
     --timeout 120000
   ```

#### Options

- `--url <url>`: Target URL (default: `https://claude.ai`)
- `--headless`: Run browser in headless mode (default: shows browser)
- `--output <dir>`: Output directory (default: `./extractions`)
- `--timeout <ms>`: Navigation timeout in milliseconds (default: `60000`)

## What Gets Extracted

The extraction includes:

1. **LocalStorage**: All conversation-related data stored in the browser
2. **IndexedDB**: Conversation databases and message stores
3. **API Data**: Fresh conversation data from Claude's API (if accessible)

## Output Format

```json
{
  "metadata": {
    "platform": "claude-ai-web",
    "extracted_at": "2025-11-29T10:00:00.000Z"
  },
  "sources": {
    "localStorage": {
      "data": { ... }
    },
    "indexedDB": {
      "data": { ... }
    },
    "api": {
      "conversations": [ ... ]
    }
  }
}
```

## Troubleshooting

### Puppeteer Installation Issues

If you encounter Chrome download errors in restricted environments:

1. **Use Method 1** (Browser Console) instead
2. **Or skip Puppeteer download** and use system Chrome:
   ```bash
   PUPPETEER_SKIP_DOWNLOAD=true npm install puppeteer-core
   ```
   Then modify `run_extraction.js` to use system Chrome

### Login Required

If the script detects you're not logged in:
- It will wait up to 5 minutes for you to log in manually
- A browser window will open where you can complete authentication
- After login, extraction proceeds automatically

### Empty Extraction

If the extraction is empty:
- Ensure you're logged into Claude
- Check that you have conversations in your account
- Verify browser permissions allow IndexedDB access

## Security Notes

- **Never share** extraction files containing sensitive conversations
- Store extractions securely (they contain your conversation history)
- Use encryption for long-term storage of extraction data
- Be cautious when running extraction scripts from untrusted sources

## Use Cases

- **Backup**: Regular backups of important conversations
- **Migration**: Moving conversations between accounts/platforms
- **Analysis**: Analyzing conversation patterns or extracting insights
- **Archival**: Long-term storage of research conversations
- **Development**: Testing conversation import/export features

## Files

- `extract_claude_web.js`: Browser-executable extraction script
- `run_extraction.js`: Automated Puppeteer runner (requires npm install)
- `README_extraction.md`: This documentation

## License

MIT - See repository LICENSE file

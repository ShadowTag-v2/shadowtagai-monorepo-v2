# Rule 09: Build Pipeline Secrets Audit

The source map shipped because nobody set sourceMap: false in the build config. That's a one-line tsconfig fix. Everybody talking about what was in the code. The real lesson: your build pipeline needs a secrets/asset audit before every release. Source maps are the obvious one — but what else is in your npm package that shouldn't be?

## Pre-Release Checklist
- Verify `sourceMap: false` in tsconfig.json/build config
- Check `.npmignore` or `files` allowlist in package.json
- Scan for `.map` files in build output
- Audit for leaked env vars, API keys, internal URLs
- Check for .env files, private keys, credentials in the package
- Verify no internal documentation or comments reference proprietary systems

## The Engineering Lesson Everyone Is Missing
The biggest insight isn't in the code. It's in the gap between building and shipping. Anthropic built 23 bash security checks, a 3-layer memory architecture, and prompt cache boundary engineering... Then shipped it with a missing .npmignore line, a public R2 bucket with no auth, and their 3rd source map leak in 13 months.

"The sophistication of what you build is independent of the reliability of how you ship it."

Add a CI check for .map files. Use a files allowlist in package.json. Takes 5 minutes. Prevents this entire class of failure.

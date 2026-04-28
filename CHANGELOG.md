# Changelog

## [v12.3] - 2026-04-28

### KovelAI Deployment Integrity Audit
- audit(build): Next.js 16.2.1 (Turbopack) — compiled 1.83s, 4/4 static pages ✅
- audit(lighthouse): A100/BP100/SEO100 — 51 passed, 0 failed ✅
- audit(ruff): F401/F841 — all checks passed, zero dead Python code ✅
- audit(biome): 28 files, 4 warnings (non-critical), format auto-fixed (quote style) ✅
- audit(guillotine): v9.0 full sweep — all passes clean ✅
- audit(cloud-run): counselconduit-00045-kjp active, Ready=True ✅
- audit(csp): firebase.json CSP headers validated — Stripe/GA/GTM/Cloudflare domains ✅
- audit(design): DESIGN.md Sovereign Architect v1.0 — no-line rule + Inter tokens aligned ✅
- feat(stitch): 2 LinkedIn campaign banners generated (project 9243896103844268571)
  - Screen `ed27dbee...` — "Your client's research is discoverable. Unless it isn't."
  - Screen `7ace1ed3...` — "Shield your client's research from discovery."
- feat(changelog): KovelAI-specific CHANGELOG.md created at apps/kovelai/CHANGELOG.md

## [v12.2] - 2026-04-25

- fix(truth): reconcile skill fleet count across 4 surfaces (AGENTS.md, GEMINI.md ×2, manifest) to 247 active (54 WS + 210 global − 17 overlap)
- fix(truth): daemon path pnkln-evolve.py → pnkln_evolve.py (underscore) in GEMINI.md
- fix(truth): manifest skill_duplicates 0→17, skill_count_agent 51→54, global 209→210
- chore(version): GEMINI.md v11.0 → v11.1
- audit(skills): 20 archived in _archive_redundant_2026-04-25/, 11/17 overlaps have redirect stubs
- audit(repos): 88 external repos, 21 unreferenced candidates for pruning
- audit(extractors): deep_browser_extractor.js (45L) is a slim JS wrapper; 11x_browser_extractor.py (191L) is canonical
- audit(dead-code): ruff F401/F841 clean across all scripts/
- audit(KI): 25 KI directories, no knowledge.lock file (integrity via directory existence)
- audit(beads): 4 entries in issues.jsonl, all RESOLVED
- audit(risk): 46 entries in RISK_REGISTER.md (last: #46)
- audit(ruff): pnkln_evolve.py passes ruff check + format
- audit(community): 1,415+ is skills.sh community total (accurate as community metric)
- audit(manifest): stale skill counts corrected
- audit(biome): cloner template has no TS files in expected path (0 files checked)
- audit(pytest): 504 tests collected — baseline holds ✅
- audit(mcp): 8 servers configured, 2 local paths ✅, 4 npm package refs (runtime-resolved), 2 core

## [v12.1] - 2026-04-25

- fix(truth): Stage 3 canonicalization — align manifest v12.0→v12.1 with 7 drift corrections
- fix(truth): gold_master_tag v11.9→v11.7 (actual latest tag), risk_register_count 86→94
- fix(truth): skill counts agent 49→51, global 224→209, duplicates 7→0 (all resolved)
- fix(truth): CI workflow count 74→75, Lighthouse labels desktop (not mobile)
- fix(secrets): prodding_engine.py api_key="TBD" → os.getenv("TESLA_API_KEY") compliance
- audit(lighthouse): kovelai A100/BP96/SEO100, shadowtagai A100/BP96/SEO100 (improved A93→A100)
- audit(tests): 504 collected, 499 passed, 3 skipped, 2 xfailed (full suite verified)
- audit(ruff): 0 F401/F841 violations across apps/libs/scripts/tests
- chore(branches): deleted stale merged branch feat/design-spec-gold-standard

## [v11.3-gold] - 2026-04-24

- fix(truth): canonicalize .NET version across all truth surfaces (11.0 Preview→10.0.106, matching global.json + csproj)
- fix(truth): update test baseline to 504 collected / 480 unit passed / 3 skipped (pytest 3.14)
- fix(truth): align gold_master_tag v11.2→v11.3, dotnet_version 10.0.202→10.0.106 in manifest
- audit(firebase): project health verified — 2 Firestore DBs (PITR+delete protection), 1 web app ACTIVE
- audit(lighthouse): kovelai.web.app A94/BP100/SEO100, shadowtagai.web.app A95/BP96/SEO100
- audit(ruff): 0 F401/F841 violations in apps/tests/scripts
- audit(pre-commit): betterleaks + detect-private-key + ruff + check-yaml all verified

## [v11.0-obsidian] - 2026-04-23

- chore(sweep): V11 items 1-22 — biome vendor exclude, .NET 10.0.106 truth, print→logging, npm audit, k6 load test
- fix(pyright): V10 Epistemic Airgap — add all Python source roots to extraPaths + executionEnvironments
- chore(sweep): items 2-7 — firebase-admin upgrade + print cleanup + Knip dead code removal

## [v11.0-obsidian] - Initial Release

- fix(sweep): V11 remainder — ast-grep rule fix + pre-commit biome fix + project ID alignment
- feat(obsidian): V11 Obsidian Release — Lighthouse Budget + 11x Extractor + IDE Governance
- feat(security): V10 Epistemic Airgap — Zero-Trust Cognitive Routing
- fix(truth): align .NET version across all 5 truth surfaces to 10.0.202
- feat(ci): V7/V8 GitOps Ascension — Zero-Trust CI + AST-Grep + Debt Burn
- feat(omega): V5+V6 Omni-Sanitation + IDE Stabilization + Omega Egress
- feat: V4 cognitive-structural-synthesis + 22-item sweep
- refactor: ruff 828→0 debt eradication + pre-commit scope fix
- feat: 22-item hardening sweep + cognitive structural synthesis
- ci(hygiene): add vulture CI gate + fix pre-commit ruff exclusions + py3.9 compat

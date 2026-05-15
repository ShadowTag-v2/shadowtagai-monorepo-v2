# Obsidian Hardened State — Post-Migration (2026-05-15)
1. **Canonical Repo**: `https://github.com/ShadowTag-v2/shadowtagai-monorepo-v2.git` (sovereign primary)
2. **Archived**: `Monorepo-Uphillsnowball` — READ-ONLY. Do NOT push.
3. Cloud Run uses old image; MUST use `try/except ImportError` for `uuid7` fallback.
4. .NET 11.0.100-preview.3 IS CONFIRMED INSTALLED. SK 1.74.0. `OnExternalEvent` is correct API.
5. Semantic Kernel Process.cs: `OnExternalEvent` is CORRECT for v1.21.0-alpha.
6. We maintain 247 active skills (54 workspace + 210 global − 17 overlap).
7. **Prompt Repetition (arXiv 2512.14982):** Applies ONLY to non-reasoning tiers to boost accuracy.
8. **GitHub Auth**: App PEM exclusive (ID 3018200). SSH primary transport. No PATs, no `gh auth login`.

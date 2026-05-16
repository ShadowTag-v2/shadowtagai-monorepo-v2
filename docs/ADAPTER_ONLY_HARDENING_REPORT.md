# ADAPTER_ONLY_HARDENING_REPORT.md

## Canonical truth files
- workspace truth: `monorepo_manifest.yaml`
- MCP truth: `antigravity-mcp-config.json`
- checklist truth: `fold_in_checklist.yaml`

## MCP surface classification
- canonical: `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity-mcp-config.json` (canonical)
- retired: `/Users/pikeymickey/.gemini/antigravity/mcp_config.json` (retired)
- adapter-only: `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.vscode/cline_mcp_settings.json` (adapter-only)

## Canonical root status
### Present canonical roots
- `apps/pnkln-stack_stack/pnkln-stack-fastapi-services`
- `apps/pnkln-stack_stack/cosmic-crab-payload`
- `apps/pnkln-stack_stack/Pipeline`
- `apps/pnkln-stack_stack/nascent-apollo`

### Missing canonical roots
- none

## Reference repo status
### Present reference repos
- `reference/public-demos/antigravity-go`
- `reference/public-demos/codepmcs`
- `reference/public-demos/judge6`
- `reference/public-demos/kosmos`
- `reference/public-demos/shadowtag_v2`

### Missing reference repos
- none

## Duplicate live root status
- result: **PASS**

## Nested git status
- result: **PASS**

## Stale model audit
- expected model family: `gemini-3.1-family`
- findings: **16730**

### Sample stale model hits
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/02_stale_model_audit.md:13:- `gemini-2.5-pro`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/02_stale_model_audit.md:21:- `MODEL_NAME = "gemini-3.1-family"`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/02_stale_model_audit.md:22:- constructor default `model: str = "gemini-3.1-family"`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/02_stale_model_audit.md:29:- `gemini-2.5-pro`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/src/core/swarm_controller.py:7:    def __init__(self, model_name="gemini-3.1-flash-lite-preview"):
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/architecture/Aegaeon_Protocol.md:7:Here is the architectural blueprint to pool 7 concurrent instances of gemini-3.1-flash-lite-preview to replicate Aegaeon's token-level auto-scaling and achieve an ~84% reduction in operational spend.
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/architecture/Aegaeon_Protocol.md:16:Aegaeon maps individual requests dynamically. We replicate this in our FastAPI backend by creating an Agent Swarm Router that treats 7 different gemini-3.1-flash-lite-preview endpoints as a single logical pool.
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/architecture/Aegaeon_Protocol.md:23:* Instance 1-5 (The Fast Path): Pure, high-speed extraction and rapid PR formatting. Routed 100% to gemini-3.1-flash-lite-preview. Because they all point to the same Context Cache, Google's backend treats them essentially as parallel decodes from a hot VRAM slab.
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/architecture/Aegaeon_Protocol.md:24:* Instance 6-7 (The Heavy Lift): If Instances 1-5 detect a deep architectural anomaly (e.g., a hardware matrix constraint violation), they escalate the pointer to gemini-3.1-family (or the Tier 3 ANE Bridge).
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/architecture/Aegaeon_Protocol.md:29:3. Savings: You pay for the 1M token cache creation, plus the heavily discounted 7M "cached token" read rate. When combined with the ultra-low baseline cost of gemini-3.1-flash-lite-preview, your net operational spend drops by roughly 80-84% compared to linear, stateless API usage.
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/Cor.Gemini.Aegaeon.Protocol.md:58:Treat several concurrent `gemini-3.1-flash-lite-preview` calls as one logical worker pool.
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/Cor.Gemini.Aegaeon.Protocol.md:72:`gemini-3.1-flash-lite-preview` for:
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity_gca_repo_bundle/AGENTS.md:14:- Default reasoning model for Antigravity and Gemini Code Assist in this repo: `gemini-3.1-pro`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/01_thread_mining_report.md:29:- recursive agent model `gemini-2.5-pro`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/01_thread_mining_report.md:37:- `MODEL_NAME = "gemini-3.1-family"`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/01_thread_mining_report.md:38:- constructor default `model: str = "gemini-3.1-family"`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/ANTIGRAVITY_CONTROL_PLANE.md:46:- model: `gemini-3.1-flash-lite-preview`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:14:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:20:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:26:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:32:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:38:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:44:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:50:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:56:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:62:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:68:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:74:      "match": "gemini-3.1-pro",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:80:      "match": "gemini-3.1-pro",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:86:      "match": "gemini-3.1-pro",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:92:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:98:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:104:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:110:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:116:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:122:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:128:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:134:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:140:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:146:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:152:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:158:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:164:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:170:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:176:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:182:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:188:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:194:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:200:      "match": "gemini-3.1-flash-lite-preview",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:206:      "match": "gemini-3.1-flash-lite-preview",

## Stale project audit
- expected project: `shadowtag-omega-v4`
- findings: **2023**

### Sample stale project hits
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity_github_app_policy.md:16:- `apps/shadowtag-web`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/test_jwt.py:5:pem_path = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/rebuilt_antigravity_bundle/antigravity_github_app_policy.md:16:- `apps/shadowtag-web`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/rebuilt_antigravity_bundle/antigravity_util_rules.yaml:18:    - "@.agent/rules/shadowtag-laws.md"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/rebuilt_antigravity_bundle/antigravity_util_rules.yaml:40:      private_key_path: "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/1_architect.sh:3:echo "🍏 [Phase 1] The Architect: Structuring 'shadowtag-omega-v2'..."
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/bundles/four_file_repo_audit_bundle/03_stale_mcp_and_naming_audit.md:22:- older project id `shadowtag-omega-v2`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity_manifest_bundle_v3/fold_in_repo_checklist.py:28:    r"shadowtag-omega-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity_manifest_bundle_v3/fold_in_repo_checklist.py:29:    r"shadowtag-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity_manifest_bundle_v3/fold_in_repo_checklist.py:36:    r"\bshadowtag-v2\b",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/manifests/monorepo_manifest.yaml:35:      path: apps/shadowtag-web
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/manifests/monorepo_manifest.yaml:68:  web: apps/shadowtag-web
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/bundles/four_file_repo_audit_bundle/01_thread_mining_report.md:51:   There are still references to old roots and old project ids like `shadowtag-omega-v2` in deployment code.
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/gen_and_set_token.py:2:pem_path = '/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem'
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/bundles/four_file_repo_audit_bundle/04_replan_and_patch_queue.md:36:- `shadowtag-omega-v2`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/bundles/four_file_repo_audit_bundle/04_replan_and_patch_queue.md:40:- `deploy_apigee_mcp.sh` backups show `shadowtag-omega-v2` still present
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/bundles/antigravity_manifest_bundle_v3/antigravity_manifest_bundle_v3/fold_in_repo_checklist.py:28:    r"shadowtag-omega-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/bundles/antigravity_manifest_bundle_v3/antigravity_manifest_bundle_v3/fold_in_repo_checklist.py:29:    r"shadowtag-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/bundles/antigravity_manifest_bundle_v3/antigravity_manifest_bundle_v3/fold_in_repo_checklist.py:36:    r"\bshadowtag-v2\b",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/bundles/antigravity_rebuilt_bundle_2026_03_18/rebuilt_antigravity_bundle/antigravity_github_app_policy.md:16:- `apps/shadowtag-web`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/01_thread_mining_report.md:51:   There are still references to old roots and old project ids like `shadowtag-omega-v2` in deployment code.
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/bundles/antigravity_rebuilt_bundle_2026_03_18/rebuilt_antigravity_bundle/antigravity_util_rules.yaml:20:    - "@.agent/rules/shadowtag-laws.md"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/bundles/antigravity_rebuilt_bundle_2026_03_18/rebuilt_antigravity_bundle/antigravity_util_rules.yaml:44:      private_key_path: "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/antigravity_github_app_policy.md:16:- `apps/shadowtag-web`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/uv.lock:1119:name = "shadowtag-omega-v2-monorepo"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/DEDUP_MAPPING.md:77:| `~/.gemini/antigravity/Monorepo-Uphillsnowball/reference/public-demos/ShadowTag-v2/shadowtag-web/.next/standalone/pnkln-stack-stack/ShadowTag-v2` | `NONE` | Non-Git Folder / Flat Copy |
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/DEDUP_MAPPING.md:151:| `~/pnkln-stack-stack/archive_legacy_ShadowTag-v2/shadowtag-web/.next/standalone/pnkln-stack-stack/ShadowTag-v2` | `NONE` | Non-Git Folder / Flat Copy |
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/pnkln_antigravity_architecture.md:79:1. **Write:** Agent writes experiment scripts to `apps/shadowtag-core/experiments/`.
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/pnkln_antigravity_architecture.md:80:2. **Build:** Agent uses Bazel: `bazel build //apps/shadowtag-core:run_exp`.
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/docs/toolbelt.md:5:- **Session Init:** Execute `/omega-loop` at the beginning of each session, as well as: `@.agent/workflows/live-engine.md`, `@.agent/docs/toolbelt.md`, `@.agent/rules/shadowtag-laws.md`.
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5956:      "match": "shadowtag-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5957:      "pattern": "\\bshadowtag-v2\\b"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5962:      "match": "shadowtag-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5963:      "pattern": "\\bshadowtag-v2\\b"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5968:      "match": "shadowtag-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5969:      "pattern": "\\bshadowtag-v2\\b"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5974:      "match": "shadowtag-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5975:      "pattern": "\\bshadowtag-v2\\b"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5980:      "match": "shadowtag-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5981:      "pattern": "\\bshadowtag-v2\\b"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5986:      "match": "shadowtag-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5987:      "pattern": "\\bshadowtag-v2\\b"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5992:      "match": "shadowtag-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5993:      "pattern": "\\bshadowtag-v2\\b"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5998:      "match": "shadowtag-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:5999:      "pattern": "\\bshadowtag-v2\\b"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:6004:      "match": "shadowtag-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:6005:      "pattern": "\\bshadowtag-v2\\b"
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:6010:      "match": "shadowtag-v2",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.json:6011:      "pattern": "\\bshadowtag-v2\\b"

## Inline secret audit
- candidate findings: **4512**

### Sample secret candidates
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/colab_worker.ipynb:120:    "os.environ[\"GEMINI_API_KEY\"] = \"AIzaSyBAJuLUQwDtMVSM5YPHpEaRVLXwuRuH7UI\"\n",
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:426:- `docs/AUDIT_REPORT.json:6018` -> `AIzaSyBAJuLUQwDtMVSM5YPHpEaRVLXwuRuH7UI`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:427:- `docs/AUDIT_REPORT.json:6024` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:428:- `docs/AUDIT_REPORT.json:6030` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:429:- `docs/AUDIT_REPORT.json:6036` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:430:- `docs/AUDIT_REPORT.json:6042` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:431:- `docs/AUDIT_REPORT.json:6048` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:432:- `docs/AUDIT_REPORT.json:6054` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:433:- `docs/AUDIT_REPORT.json:6060` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:434:- `docs/AUDIT_REPORT.json:6066` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:435:- `docs/AUDIT_REPORT.json:6072` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:436:- `docs/AUDIT_REPORT.json:6078` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:437:- `docs/AUDIT_REPORT.json:6084` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:438:- `docs/AUDIT_REPORT.json:6090` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:439:- `docs/AUDIT_REPORT.json:6096` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:440:- `docs/AUDIT_REPORT.json:6102` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:441:- `docs/AUDIT_REPORT.json:6108` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:442:- `docs/AUDIT_REPORT.json:6114` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:443:- `docs/AUDIT_REPORT.json:6120` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:444:- `docs/AUDIT_REPORT.json:6126` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:445:- `docs/AUDIT_REPORT.json:6132` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:446:- `docs/AUDIT_REPORT.json:6138` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:447:- `docs/AUDIT_REPORT.json:6144` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:448:- `docs/AUDIT_REPORT.json:6150` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:449:- `docs/AUDIT_REPORT.json:6156` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:450:- `docs/AUDIT_REPORT.json:6162` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:451:- `docs/AUDIT_REPORT.json:6168` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:452:- `docs/AUDIT_REPORT.json:6174` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:453:- `docs/AUDIT_REPORT.json:6180` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:454:- `docs/AUDIT_REPORT.json:6186` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:455:- `docs/AUDIT_REPORT.json:6192` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:456:- `docs/AUDIT_REPORT.json:6198` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:457:- `docs/AUDIT_REPORT.json:6204` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:458:- `docs/AUDIT_REPORT.json:6210` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:459:- `docs/AUDIT_REPORT.json:6216` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:460:- `docs/AUDIT_REPORT.json:6222` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:461:- `docs/AUDIT_REPORT.json:6228` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:462:- `docs/AUDIT_REPORT.json:6234` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:463:- `docs/AUDIT_REPORT.json:6240` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:464:- `docs/AUDIT_REPORT.json:6246` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:465:- `docs/AUDIT_REPORT.json:6252` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:466:- `docs/AUDIT_REPORT.json:6258` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:467:- `docs/AUDIT_REPORT.json:6264` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:468:- `docs/AUDIT_REPORT.json:6270` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:469:- `docs/AUDIT_REPORT.json:6276` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:470:- `docs/AUDIT_REPORT.json:6282` -> `AIzaSyABC123456789abcdefghijk`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:471:- `docs/AUDIT_REPORT.json:6288` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:472:- `docs/AUDIT_REPORT.json:6294` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:473:- `docs/AUDIT_REPORT.json:6300` -> `AIzaSyBwwM0EXAMPLEKEY1234567890`
- /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/docs/AUDIT_REPORT.md:474:- `docs/AUDIT_REPORT.json:6306` -> `AIzaSyDi-JrXjIdZhw9QyDffwuwe_Kun87aRBBA`

## Blockers
- none

## Final verdict
- **COMPLETE**

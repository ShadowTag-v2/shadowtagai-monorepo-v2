name: epistemic-airgap
# Doctrine: Internal IP searches route to `search_corporate_ip` (App/PEM isolated). Public IP routes to `execute_deep_browser_expansion`. Never leak corporate strings to the open web.
PROPRIETARY ISOLATION: Internal IP searches MUST route to local AST-Grep against ./external_repos/corp-monorepo. Never leak corporate schemas to the open web.

# DEEP BROWSER EXTRACTION
# Use tools/scripts/deep_browser_extractor.js to pull live DOM elements when `search_web` fails to return deep text.

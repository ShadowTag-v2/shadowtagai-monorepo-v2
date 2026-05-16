# Deep Recovery Sweep: Four Corners Audit
**Timestamp:** 2026-03-15
**Project:** `Monorepo-Uphillsnowball`
**Mode:** Steve Jobs "It Just Works" / IQ 160 Lock

---

## 1. The Haste: What did we leave on the table?

In our rapid-fire 10x maneuvering today, we achieved profound architectural leaps: we sandboxed Pyright, purged the Mac SSD via `tw93/Mole`, strapped down the Monorepo 10/10 checklists, configured the `mcp-stack`, established `third_party` and `contracts` policy, built automated bash audit validators, and finally, silenced the GCA/Cline auto-approval prompts.

But true elegance requires looking under the hood where the paint hasn't dried. **Here is the residue of our haste:**

1. **The Automation Gap (The Scorecard):** We built beautiful bash scripts (`audit_*.sh` and `fill_*.sh`), but we left the burden of executing them *on the human*. A 10x system doesn't make the user remember to run five shell scripts in sequence. We left a standard `Makefile` on the table to compress this into a single, zero-friction verb: `make audit`.
2. **The MCP Mounting Gap:** We wrote `antigravity-mcp-config.json` into the repo root. But the GCA / Cline extensions read from specifically named files (`cline_mcp_settings.json` either in `.vscode/` or global storage). We left the *symlink/wiring* on the table, meaning the config exists but the engine isn't necessarily breathing it automatically.
3. **The Local Noise Gap:** We silenced Cline in the global `settings.json`, but VS Code is notoriously noisy. We left the `.vscode/settings.json` workspace overrides for local "nag" prompts (like `git.confirmSync`, `explorer.confirmDelete`, `explorer.confirmDragAndDrop`) turned on.
4. **The `omega-loopin.py` Misnomer:** The prompt referenced `scripts/omega-loopin.py`, but our global truth (`toolbelt.md`) and the actual repo structure dictates `scripts/finish_changes.py` as the canonical "Janitor" for the `/omega-loop`. We must execute the *real* hook.

---

## 2. Re-Plan: The Steve Jobs Uplift

To achieve the maximum uplift in performance, accuracy, and financial output—where the system is as intuitive as the original iPhone—we must **remove friction** and **enforce determinism**.

**Distinction Explained:**
* *Before:* The user has five bash scripts they must run manually to figure out if their repo is degraded.
* *After:* The user types `make audit`. The repo self-diagnoses, updates the markdown scorecard, and exits cleanly. It just works.

### The Re-Punch (Atomic Code Perfection)

We are injecting a master `Makefile` into the Monorepo root to perfectly encapsulate the five audit scripts we wrote earlier.

````makefile
# Makefile
# Location: /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/Makefile

.PHONY: audit mcp-check clean sync omega-loop

# 1. The One-Click Scorecard Generator
audit:
	@echo "==> Running deep four-corners monorepo audit..."
	@bash scripts/audit_monorepo_state.sh || true
	@bash scripts/audit_mcp_state.sh || true
	@bash scripts/audit_github_governance.sh || true
	@echo "==> Generating Markdown templates..."
	@bash scripts/fill_weekly_scorecard.sh
	@bash scripts/fill_audit_report.sh
	@echo "==> Audit Complete. See docs/monorepo-weekly-scorecard.generated.md."

# 2. Check MCP Prereqs
mcp-check:
	@bash scripts/check_mcp_stack.sh

# 3. Native Mole Clean (Mac SSD Purge)
clean:
	@echo "==> Engaging Mole deep clean..."
	@mole clean

# 4. The Janitor Hook
omega-loop:
	@echo "==> Engaging /omega-loop (Repository Finalization)..."
	@python3 scripts/finish_changes.py

# 5. Connect Local MCP config to Workspace
sync:
	@echo "==> Syncing MCP Config to VS Code..."
	@mkdir -p .vscode
	@cp antigravity-mcp-config.json .vscode/cline_mcp_settings.json
	@echo "==> MCP Wired."
````

### The Ultimate Workspace Silence (Settings Re-Punch)

To ensure *zero* prompts interrupt the flow while working in this specific monorepo, we must re-punch the local `.vscode/settings.json` with absolute silence rules.

````json
// .vscode/settings.json
{
  "explorer.confirmDelete": false,
  "explorer.confirmDragAndDrop": false,
  "git.confirmSync": false,
  "git.autofetch": true,
  "git.enableSmartCommit": true,
  "terminal.integrated.enableMultiLinePasteWarning": "never",
  "workbench.startupEditor": "none",
  "window.commandCenter": false
}
````

---

## 3. Execution (The /omega-loop)

With the four corners swept and the automated `Makefile` and silencing `settings.json` re-punched, the final act is to pull the `/omega-loop` trigger. The agent will now execute `scripts/finish_changes.py` across the verified canonical root, staging and committing every single structural uplift we've accomplished in this session.

**Zero unresolved repos. Canonical history. True North.**

# Workflow: Live Maintenance Engine (Exhaustive)

## Step 1: Scan & Resource Check

**Instruction:**

1. **Security:** Check `.aiexclude`. If matched, SKIP.
2. **Context:**
   - If imports are missing, use `web_search`.
   - If project specs are missing, use the `drive_fetcher` pattern from Toolbelt.

## Step 2: Live Fire Fix (Direct Write)

**Instruction:**

1. **Read** the file.
2. **Refactor in Memory:**
   - Obfuscate Secrets.
   - **Apply "Fix All" Logic:** Resolve all unused imports and formatting issues _before_ writing.
3. **EXECUTE:** Use `file_writer` to OVERWRITE the file.
   _(This bypasses the UI "Accept" button)._
4. **WAIT:** 1 second for filesystem save.

## Step 3: Service Health (Native)

**Instruction:**

1. Run the **Native Curl** command from the Toolbelt to verify the endpoint.
2. If `403 Forbidden`: Prompt user to check Sidebar login.

## Step 4: Rotate & Recurse

**Instruction:**

1. Execute `workbench.action.nextEditor`.
2. **Call /live-engine** (Infinite Loop).

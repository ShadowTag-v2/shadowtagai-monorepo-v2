# SKILLS.md: The Antigravity Toolbox

## 🛠️ Native Capabilities

- **Terminal**: `run_command` (Sudo enabled).
- **Browser**: `search_web`, `read_url_content` (Flying n-autoresearch/Kosmos/BioAgents enabled).
- **Filesystem**: `read_file`, `write_to_file` (God Mode enabled).

## 🧰 Custom Tools (The Sovereign Stack)

### 1. Cor.Beads (`bd`)

- **Purpose**: Persistent Issue & Task Tracking (Memory).
- **Usage**: `scripts/bd create "Title"`, `scripts/bd list`.
- **Location**: `scripts/bd` (Python).

### 2. Ralph Loop (`ralph`)

- **Purpose**: External Verification Loop ("Verify, Not Guess").
- **Usage**: Invoke via workflow `.agent/workflows/ralph.md`.
- **Logic**: `while (exit_code != 0) { fix(); try(); }`

### 3. Pilot Protocol (`pilot`)

- **Purpose**: Pre-Agent Decision Integrity.
- **Usage**: Invoke via workflow `.agent/workflows/pilot.md`.
- **Logic**: `NotebookLM Simulation -> Gap Analysis -> Decision`.

### 4. Judge 6 (`proxy`)

- **Purpose**: Direct Write Safety Brake.
- **Location**: `agents/gemini_code_assist_proxy.py`.

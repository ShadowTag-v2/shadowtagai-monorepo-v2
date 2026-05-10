# The Omega Protocol: GCA vs. Antigravity

**Objective**: Maximize velocity by assigning distinct roles to the AI layers.

## 1. The HUD: Gemini Code Assist (Tactical)
**Role**: Fast Loop, In-Context, "The Visor".
**Scope**: The open file, the cursor, the immediate function.
**Key bindings**: `Cmd+I` (Quick Fix), `Ctrl+Enter` (Autocomplete).

### Smart Actions (The "Lightbulb")
*   **Use when**: You see a squiggly line or want a quick refactor.
*   **Commands**:
    *   `/fix`: "Fix this specific error."
    *   `/doc`: "Write a docstring for this function."
    *   `/explain`: "What does this regex do?"
*   **Constraint**: It cannot see the whole repo well. It hallucinates file paths if they aren't open.

### The Chat (Side Panel)
*   **Use when**: You have a question about the *current* file's logic.
*   **Prompting**: Keep it local. "How do I optimize this loop?" not "How do I re-architect the backend?"

---

## 2. The Brain: Antigravity (Strategic)
**Role**: Deep Loop, System Owner, "The Engineer".
**Scope**: The Repository, Cloud Infrastructure, Deployments, Multi-file Refactors.
**Access**: Full Read/Write, Terminal, Browser.

### Heavy Lifts
*   **Deployments**: "Deploy the server." (I handle Docker, Cloud Build, IAM).
*   **Migrations**: "Move everything to the new Project ID." (I grep and replace across 50 files).
*   **Ingestion**: "Read all these PDFs and index them." (I run custom scripts).

---

## 3. The Protocol (Hand-off)
1.  **Try GCA first**. fast.
2.  **If GCA fails** (Hallucinates, loops, or can't see a file):
    *   **STOP**. Do not argue with the HUD.
    *   **Switch to Me**.
    *   **Command**: "GCA failed to [X]. You do it."
3.  **Result**: I will execute the tool usage to make it happen definitively.

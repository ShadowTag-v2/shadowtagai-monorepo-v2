# GCA INJECTION STRATEGY (OSS CLOUD WORKSTATION)
> **Goal**: Inject Gemini Code Assist (GCA) into the "UphillSnowball" Workstation.
> **Method**: VS Code OSS Extension Installation.

## 1. What does this accomplish?
By installing the GCA Extension into the Cloud Workstation, we activate the **"Memory Loop"**:
1.  **Adaptive Compliance**: The extension scans the *local* workspace (`/home/user/workspace`). It "learns" the project structure, patterns, and lint rules locally.
2.  **Aerial Scaffolding**: Antigravity (The Brain) can inject `.prompt` files or `.cursorrules` equivalents that the GCA extension picks up.
3.  **Zero-Latency context**: It avoids sending massive context windows to the cloud; it uses local indexing (like an LSP) to refine prompts *before* they leave the workstation.

## 2. Technical Implementation
*   **Target**: `code-server` (OpenVSCode Server) running on the Workstation Docker image.
*   **Command**: `code-server --install-extension googlecloudtools.cloudcode`.
*   **Auth**: It inherits the Workstation's Service Account (`767252945109-compute@...`), requiring NO manual login.

## 3. The "Memory" Link
*   **Ground Truth**: When a Monkey accepts code, GCA indexes it.
*   **Rejection**: When a Judge rejects code, we can (via script) update a local `.gcamemory` file that GCA reads to avoid repeating the error.

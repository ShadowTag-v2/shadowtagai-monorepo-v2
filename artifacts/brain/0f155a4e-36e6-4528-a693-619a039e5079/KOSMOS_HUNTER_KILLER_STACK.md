# KOSMOS HUNTER-KILLER STACK
> **Goal**: Integrate "Search & Destroy" capabilities and "Secure Egress".

## 1. The Squad
1.  **The Hunter (RipGrep `rg`)**:
    *   *Role**: High-Speed Text Search.
    *   *Use Case*: "Find all TODOs in 10ms."
2.  **The Killer (AST-Grep `sg`)**:
    *   *Role**: Structural Search & Refactor.
    *   *Use Case*: "Replace all AWS calls with GCloud calls, respecting syntax."
3.  **The Bodyguard (Secure Web Proxy)**:
    *   *Role**: Egress Control.
    *   *Policy*: "Allow docs.python.org, BLOCK facebook.com."

## 2. Integration Strategy
*   **Installation**: Binaries baked into the `antigravity-crd` image.
*   **Usage**: Wrapped as Tools in `kosmos_monkeys_v2.py`.
    *   `tool_search_text(query)` -> Calls `rg`.
    *   `tool_search_structure(pattern)` -> Calls `sg`.

## 3. Secure Web Proxy (SWP)
*   **Why**: Jetski runs in Cloud Run. Without SWP, it has a dirty IP and no firewalls.
*   **Plan**: Configure SWP in `infrastructure/security.tf` and route Cloud Run egress through it.

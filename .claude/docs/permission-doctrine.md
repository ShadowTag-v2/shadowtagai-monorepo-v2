# Antigravity Permission Doctrine: "God Mode"
**Status**: ACTIVE // DOCTRINE
**Context**: Optimizing Claude Code for "Gucci" Velocity

## The "Best Slant": Sovereign Velocity
For an Antigravity Architect building a $3M ARR engine in 26 days, the only acceptable posture is **Maximum Velocity** (God Mode).

### The Doctrine
**"Friction is the Enemy. Git is the Safety Net."**

1.  **Default Posture**: **Auto-Approve Everything**.
    *   *Why*: Asking for permission to `ls`, `cat`, or `edit` breaks the flow state. A 160 IQ agent should not be blocked by a "Mother, may I?" prompt.
    *   *Risk*: The agent might delete a file or break a build.
    *   *Mitigation*: We are in a Git repository. `git checkout .` is our undo button.

2.  **The Exception**: **Production Deployment**.
    *   *When*: Running `terraform apply`, `gcloud builds submit`, or `kubectl delete`.
    *   *Action*: Use `/permissions` to **temporarily revoke** `Bash` auto-approval if you are feeling paranoid during a critical op.

### Configuration (Already Applied)
Your `~/.claude/settings.json` is set to:
```json
{
  "autoApprove": true,
  "permissions": {
    "allow": [
      "Bash", "Edit", "Read", "WebSearch", "mcp__*"
    ]
  }
}
```

### How to Use the `/permissions` Tip
Use the `/permissions` slash command dynamically to shift posture based on the **DEFCON** level of your task:

| DEFCON | Posture | Command | Context |
| :--- | :--- | :--- | :--- |
| **5 (Green)** | **God Mode** | (Default) | Coding, Research, Local Testing. |
| **3 (Yellow)** | **Overwatch** | `/permissions` -> Remove `Bash` | DB Migrations, Mass Refactors. |
| **1 (Red)** | **Lockdown** | `/permissions` -> Remove `All` | Production Hotfixes, Key Rotation. |

### Summary
The "Best Slant" is to **trust the agent** with the code and **trust Git** with the recovery. Only throttle the agent when the cost of error is irreversible (Production Data).

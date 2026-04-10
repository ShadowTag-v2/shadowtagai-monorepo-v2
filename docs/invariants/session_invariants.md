# Active Session Invariants (MEMORY LOCKED)

1. Push Method and Credentials:
   - Primary: https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball
     - PEM: /Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem
     - App ID: 3018200
     - Client ID: Iv23ctYqrxPQIt2ir8gY
   - Secondary (ehanc69): https://github.com/ehanc69
     - PEM: /Users/pikeymickey/Downloads/antigravity-manager.2026-03-13.private-key.pem
     - App ID: 3018080
     - Client ID: Iv23liWtuBLy8uYLpzjn
   - Client Secret: client_secret_767252945109-g8e1bdmvl4u2ff4mkbvhcsbbduh6kv7v.apps.googleusercontent.com.json
   - Orgs: https://github.com/orgs/ShadowTag-v2/repositories

2. Workspace Isolation Settings:
   - Workspace Definition File: .code-workspace file created at the root of the repository (.../Monorepo-Uphillsnowball/Monorepo-Uphillsnowball.code-workspace) which tells the agent exactly which folder belongs to your workspace so it doesn't wander off or create its own nested workspace context.
   - Strict Mode & Non-Workspace Configurations: ~/.antigravity/config.json contains rigid configurations to apply isolation:
     {
     "strictMode": true,
     "allowNonWorkspaceFileAccess": false
     }
   - Launch constraint: Antigravity is explicitly pointed to this directory to ensure the sandbox correctly locks the agent inside this context and eliminates path-traversal jumps outside the Monorepo-Uphillsnowball repository.

_These invariants MUST be repeated verbatim before any repo-wide action until the user says "MEMORY UNLOCK."_

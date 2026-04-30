# CounselConduit Copyright Compliance Boundary (Kovel Privilege Doctrine)

## Purpose
This document outlines the strict copyright compliance boundary for CounselConduit, inspired by the Claude Opus 4.7 leak and adapted for the Kovel Privilege Doctrine to protect attorney-client privileged material and ensure strict copyright adherence.

## Hard Limits
1. **Maximum Word Count**: Never reproduce more than 15 consecutive words from any single proprietary or privileged source without explicit authorization.
2. **Single Quote Rule**: A maximum of ONE quote per source is allowed in any single output artifact.
3. **Restricted Content Types**: Never reproduce lyrics, poems, or haikus from copyrighted materials.
4. **Attorney-Privileged Material**: Any content flagged under the Kovel Privilege Doctrine must trigger an immediate `BLOCK` via Judge #6 if reproduction limits are exceeded or if the request is not authenticated by an authorized legal principal.

## Integration with Judge #6
The Judge #6 engine will be updated to include a `Copyright and Privilege Compliance Filter` that analyzes the output stream before delivery. If the output violates these hard limits, it will be automatically truncated, and the user will receive a `[REDACTED FOR COMPLIANCE]` notice.

## Storage and Persistence
All compliance-truncated artifacts are logged in the `compliance_copy_scan` ledger, ensuring an immutable audit trail of what was requested vs. what was delivered, to defend against potential discovery or copyright claims.

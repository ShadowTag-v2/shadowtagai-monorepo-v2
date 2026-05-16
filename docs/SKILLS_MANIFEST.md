# Governed Skills Manifest

## Core Posture
This skills manifest operates inside the Antigravity Spec boundaries. All skills execution policies are subject to formal verification checks and gated procedures.

## Policy
1. **Verification-Before-Completion**: Any artifact creation or system adjustment driven by an external skill must be fully verified and idempotency-locked before completion signatures.
2. **Gated Execution**: Skills are not implicitly trusted. 
3. **Reference-Only Community Skills**: All public or community-developed skills exist purely as reference material inside `reference/skills_extraction_sources`.
4. **Four-Stage Approval Gate**: No skill may execute runtime payloads against the root environment without satisfying the following pipeline:
   - **Ingest**: Code is brought into the environment.
   - **Classify**: Intended behavior is structurally mapped against Antigravity policies.
   - **Verify**: The execution paths are stripped of potential secondary-truth surfaces.
   - **Promote**: The validated capability is mapped explicitly into the memory subsystem.

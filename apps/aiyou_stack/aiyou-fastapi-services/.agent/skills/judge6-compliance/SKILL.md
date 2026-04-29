---
name: Claude_Code_6-compliance
description: Enforces Pnkln "Judge 6" Risk Protocols (Wet Fleece/Dry Ground). Use this to validate project phases before deployment.
---

# Judge 6 Compliance Skill

This skill enforces the **Pnkln Gideon Protocol** ("Judge 6") before allowing significant actions like deployment or scaling.

## Instructions

1. **Analyze Request**: Determine the current project phase implied by the user.
   - **Phase 1 (Wet Fleece)**: Initial setup, $0 spend, technical proofs.
   - **Phase 2 (Dry Ground)**: Unit economics check, value verification.
   - **Phase 3 (Battle)**: Scaling, billing enabled.

2. **Execute Risk Assessment**:
   Run the python script to validate the phase criteria.

   ```bash
   # Syntax: python scripts/assess_risk.py <phase_number> [margin_float]
   python scripts/assess_risk.py 1
   ```

   If the user provides financial data (e.g. "We have 40% margin"), pass it:

   ```bash
   python scripts/assess_risk.py 2 0.40
   ```

3. **Interpret Result**:
   - **Exit 0**: Proceed with the user's request.
   - **Exit 1**: **BLOCK** the request. Report the error and demand optimization (e.g. "Margin too low").

## Constraints

- **NEVER** recommend `gcloud apply` or `terraform apply` if this verification fails.
- **ALWAYS** run this check when the user mentions "deploy", "scale", "spend", or "GKE".

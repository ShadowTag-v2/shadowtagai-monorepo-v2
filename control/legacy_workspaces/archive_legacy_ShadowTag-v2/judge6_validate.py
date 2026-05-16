# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from sovereign_fold import pnkln_unit_econ, pnkln_judge6_check

print(">>> RUNNING JUDGE 6 VALIDATION")
# Validate AiYou Unit Econ (Hypothetical)
econ = pnkln_unit_econ(rev=10.0, mat=1.5, lab=0.5, over=1.0)
print(f"AiYou Unit Econ: {econ}")
print(pnkln_judge6_check("AiYou", "Phase 1"))

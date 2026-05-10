from sovereign_fold import pnkln_judge6_check, pnkln_unit_econ

print(">>> RUNNING JUDGE 6 VALIDATION")
# Validate ShadowTag-v4 Unit Econ (Hypothetical)
econ = pnkln_unit_econ(rev=10.0, mat=1.5, lab=0.5, over=1.0)
print(f"ShadowTag-v4 Unit Econ: {econ}")
print(pnkln_judge6_check("ShadowTag-v4", "Phase 1"))

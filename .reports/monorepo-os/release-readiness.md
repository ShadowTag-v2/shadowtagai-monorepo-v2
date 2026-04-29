═══ Release Readiness Gate ═══

── Gate 1: SkillOps Triage ──
  ✓ Triage: All actual-risk findings mitigated
── Gate 2: Secret Scan ──
  ⚠ Secret scan: Findings detected (review .gitleaksignore)
── Gate 3: Oracle Score ──
  ✓ Oracle score: 100% (threshold: 85%)
── Gate 4: Bloat Gate ──
═══ Pre-Push Bloat Gate ═══

── Check 1: Large Staged Files (>5MB) ──
  ✓ No staged files exceed 5MB
── Check 2: Banned Extensions ──
  ✓ No banned extensions detected
── Check 3: Bloated Directories ──
  ✓ No bloat directories tracked
── Check 5: Commit Size ──
  ✓ No staged changes (dry-run mode)

═══════════════════════════════
  Result: ✅ BLOAT GATE PASSED (0 warnings)
═══════════════════════════════
  ✓ Bloat gate: Passed (fast mode)
── Gate 5: Truth File Integrity ──
  ✓ Truth files: All 8 present
── Gate 6: NDJSON Integrity ──
  ✓ NDJSON: All files valid
── Gate 7: Clean Working Tree ──
  ✓ Working tree: Clean (transient paths excluded)
── Gate 8: Guardrail Annotations ──
GUARDRAIL Annotation Audit: 12/12 annotated
All moderate+ risk skills annotated ✅
Report: .reports/skills/guardrail_annotation_audit.md
  ✓ Guardrail annotations: Complete
── Gate 9: Contract Coverage ──
  ✓ Contract coverage: 29/39 (74%)

═══════════════════════════════
  Passed: 8 | Failed: 0 | Warnings: 1
  Result: ✅ RELEASE AUTHORIZED
═══════════════════════════════

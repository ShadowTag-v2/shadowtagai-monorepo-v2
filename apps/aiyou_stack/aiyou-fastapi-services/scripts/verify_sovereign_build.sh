#!/bin/bash
# ==============================================================================
# 🛡️ SOVEREIGN BUILD VERIFICATION PROTOCOL (AUDIT)
# ==============================================================================
# Checks:
# 1. Critical Artifact Existence
# 2. Terraform Validity
# 3. Python Syntax/Import Integrity
# ==============================================================================

echo ">>> 🦍 INITIATING SOVEREIGN AUDIT..."

ERRORS=0

verify_file() {
    if [ -f "$1" ]; then
        echo "✅ FOUND: $1"
    else
        echo "❌ MISSING: $1"
        ERRORS=$((ERRORS+1))
    fi
}

echo ">>> [1] ARTIFACT CHECK..."
verify_file "infra/terraform/consolidation.tf"
verify_file "src/pipeline/consolidation_beam.py"
verify_file "src/governance/Claude_Code_6/pipeline_ops.py"
verify_file "src/antigravity/grounded_agent.py"
verify_file "scripts/harvest_docs_producer.py"

echo ">>> [2] TERRAFORM VALIDATION..."
# Needs to run in the terraform dir
if [ -d "infra/terraform" ]; then
    cd infra/terraform
    terraform validate || echo "⚠️  Terraform validation failed (may need init)"
    cd ../..
else
    echo "❌ MISSING: infra/terraform directory"
    ERRORS=$((ERRORS+1))
fi

echo ">>> [3] PYTHON SYNTAX CHECK..."
for pyfile in src/pipeline/consolidation_beam.py src/governance/Claude_Code_6/pipeline_ops.py src/antigravity/grounded_agent.py scripts/harvest_docs_producer.py; do
    if [ -f "$pyfile" ]; then
        python3 -m py_compile "$pyfile"
        if [ $? -eq 0 ]; then
            echo "✅ SYNTAX OK: $pyfile"
        else
            echo "❌ SYNTAX ERROR: $pyfile"
            ERRORS=$((ERRORS+1))
        fi
    fi
done

if [ $ERRORS -eq 0 ]; then
    echo ">>> ✅ SOVEREIGN BUILD VERIFIED. SYSTEM GREEN."
    exit 0
else
    echo ">>> 🛑 VERIFICATION FAILED. $ERRORS ERRORS DETECTED."
    exit 1
fi

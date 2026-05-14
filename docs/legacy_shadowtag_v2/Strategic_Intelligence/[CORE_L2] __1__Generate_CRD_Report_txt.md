# Original Path: # 1. Generate CRD Report/# 1. Generate CRD Report.txt

# Categories: CORE_L2

# 1. Generate CRD Report

chmod +x scripts/analyze_k8s_crds.sh
./scripts/analyze_k8s_crds.sh

# 2. View Report Summary

echo "--- REPORT SUMMARY ---"
grep -c "✅" reports/crd_inventory.md || echo "0 Installed"
grep -c "❌" reports/crd_inventory.md || echo "0 Missing"

# 3. Run CodePMCS Scanner (Now with Judges installed)

chmod +x scripts/judge_gate.py scripts/judge_seven_cost.py scripts/judge_eight_compliance.py
./scripts/run_codepmcs_local.sh

under sidebar "cloud functions" "click here to set up your current workspace for clound functions". i just enabled all necessary apis, now go back to following and re-implement all https://docs.cloud.google.com/run/docs/quickstarts/functions/deploy-functions-gcloud?_gl=1*9coxv5*_ga*NTY3MjA2NDcuMTc2NDYxMTI2NA..*_ga_WH2QY8WWF5*czE3Njc0ODA2NzgkbzYzJGcxJHQxNzY3NDgyMzEyJGozMiRsMCRoMA.. https://docs.cloud.google.com/run/docs/quickstarts/functions/deploy-functions-gcloud?_gl=1*9coxv5*_ga*NTY3MjA2NDcuMTc2NDYxMTI2NA..*_ga_WH2QY8WWF5*czE3Njc0ODA2NzgkbzYzJGcxJHQxNzY3NDgyMzEyJGozMiRsMCRoMA..

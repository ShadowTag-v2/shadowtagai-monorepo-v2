#!/usr/bin/env bash
# ==============================================================================
# pnkln-gcloud-ops.sh - PNKLN GCloud Operations Script
# Combined runner for all PNKLN SOP operations via Vertex AI
# ==============================================================================
# Usage: ./pnkln-gcloud-ops.sh [command] [options]
#
# Commands:
#   all           Run all sections sequentially
#   init          Initialize environment and test connection (00-01)
#   primer        Run PNKLN primer execution (02)
#   repo          Run repo enforcement execution (03)
#   allhands      Run all-hands execution (04)
#   sops          Echo SOP summaries (05-06)
#   valuation     Run valuation calculations (07-08)
#   drill         Run rapid drill execution (09)
#   investor      Generate investor slides (10)
#   perfile       Run per-file execution (11)
#   master        Run master macro execution (12)
#   status        Echo strategy/position/specs (13-14)
#   route         Agent router (15)
#   health        Healthcheck (16)
#
# Environment Variables:
#   GOOGLE_CLOUD_PROJECT  - GCP Project ID (required)
#   REGION                - GCP Region (default: us-central1)
#   MODEL                 - Vertex AI model (default: gemini-1.5-pro)
#   ARR                   - Annual Recurring Revenue (default: 1000000)
#   OPEX                  - Operating Expenses (default: 3000000)
#   MULT                  - Valuation Multiple (default: 10)
#   FILES                 - File list for per-file execution
#   TASK                  - Task type for agent router
# ==============================================================================

set -euo pipefail

# ==============================================================================
# 00_init - Initialize environment
# ==============================================================================
init_env() {
    PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?GOOGLE_CLOUD_PROJECT environment variable required}"
    REGION="${REGION:-us-central1}"
    MODEL="${MODEL:-gemini-1.5-pro}"
    ACCESS_TOKEN="$(gcloud auth print-access-token)"

    echo "init_ok:$PROJECT_ID@$REGION/$MODEL"
}

# Shared gen() function for Vertex AI calls
gen() {
    local prompt="$1"
    curl -s -X POST \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json; charset=utf-8" \
        "https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/publishers/google/models/$MODEL:generateContent" \
        -d "$(jq -n --arg p "$prompt" '{contents:[{role:"user",parts:[{text:$p}]}]}')"
}

# ==============================================================================
# 01_services - Enable required GCloud services
# ==============================================================================
enable_services() {
    gcloud services enable aiplatform.googleapis.com compute.googleapis.com >/dev/null 2>&1 || true
    echo "services_ok"
}

# ==============================================================================
# 02_primer_exec - Run PNKLN primer
# ==============================================================================
run_primer() {
    local PROMPT='# pnkln Primer
Operate at IQ160 metaphor; pnklnJR(purpose)+Doctrine(reason)+ARM(brakes). All-hands: digest→classify{KEEP|REFERENCE ONLY|DISCARD}→optimize→roll-up→exec summary. Enforce SOP-A..D with Bourne boosts (2× throughput,+90% safety). If conflict, voice objections per pnklnJR. Return a one-page ops stance.'

    echo "## 02_primer_exec"
    gen "$PROMPT"
}

# ==============================================================================
# 03_repo_enforcement_exec - Apply SOPs repo-wide
# ==============================================================================
run_repo_enforcement() {
    local PROMPT='Apply pnkln SOPs repo-wide: 1) UploadTriage classify+score; KEEP→tickets→ActiveResources; delta summary. 2) Change&Release premortem(5); featureflag; stressdrills; promote/rollback; postmortem<24h. 3) DecisionProtocol Decision/Context/Options/Choice(pnklnJR+Doctrine)/Risks(ARM)/Owner+By-When/Metrics. 4) CodeReview diff|tests|sec+privacy|observability|rollbackplan. Output: plan+deltas+exec summary.'

    echo "## 03_repo_enforcement_exec"
    gen "$PROMPT"
}

# ==============================================================================
# 04_all_hands_exec - Run all-hands process
# ==============================================================================
run_all_hands() {
    local PROMPT='Run pnkln All-Hands now: sort memory/docs by latest; triage {KEEP|REFERENCE ONLY|DISCARD}; streamline+optimize (pnklnJR+Doctrine+ARM); regenerate comprehensive roll-up; output "pnkln All-Hands Complete" + plain-text executive summary.'

    echo "## 04_all_hands_exec"
    gen "$PROMPT"
}

# ==============================================================================
# 05_sops_compact_echo - Echo SOP summaries
# ==============================================================================
echo_sops() {
    echo "## 05_sops_compact_echo"
    echo "SOP-A: classify{KEEP|REF|DISCARD},score0-5,KEEP→tickets→ActiveResources,delta_log"
    echo "SOP-B: premortem5→mitigate,featureflag,drills,promote/rollback,postmortem<24h"
    echo "SOP-C: Decision|Context|Options|Choice(pnklnJR+Doctrine)|Risks(ARM)|Owner+ByWhen|Metrics"
    echo "SOP-D: diff|min,tests|upd,sec+privacy,observability,rollbackplan"
}

# ==============================================================================
# 06_frameworks_echo - Echo framework boosts
# ==============================================================================
echo_frameworks() {
    echo "## 06_frameworks_echo"
    echo "FrameworkBoosts: Premortem+80%,5-Whys+90%,Postmortem2×; ARM: Hazard+85%,Controls+90%,Rollback~95%"
}

# ==============================================================================
# 07_valuation_exec - Run valuation calculation via AI
# ==============================================================================
run_valuation_ai() {
    local ARR="${ARR:-1000000}"
    local OPEX="${OPEX:-3000000}"
    local MULT="${MULT:-10}"

    local PROMPT="Compute pnkln valuation uplift. Inputs: ARR=\$${ARR}, OPEX=\$${OPEX}, Multiple=${MULT}. Assume 15–30% OPEX savings from 2× throughput,+90% safety,2× decision velocity. Map savings→ARR-equivalent; uplift=ARR-eq×Multiple. Return assumptions, math steps, sensitivity rows(15,20,25,30%)."

    echo "## 07_valuation_exec"
    gen "$PROMPT"
}

# ==============================================================================
# 08_valuation_numbers_only - Pure calculation (no AI)
# ==============================================================================
calc_valuation_numbers() {
    local ARR="${ARR:-1000000}"
    local OPEX="${OPEX:-3000000}"
    local MULT="${MULT:-10}"

    echo "## 08_valuation_numbers_only"
    for P in 15 20 25 30; do
        S=$(awk -v o="$OPEX" -v p="$P" 'BEGIN{printf "%.0f",o*p/100}')
        U=$(awk -v s="$S" -v m="$MULT" 'BEGIN{printf "%.0f",s*m}')
        printf "%s%% save:\$%'d uplift:\$%'d\n" "$P" "$S" "$U"
    done
}

# ==============================================================================
# 09_rapid_drill_exec - Create rapid drill plan
# ==============================================================================
run_rapid_drill() {
    local PROMPT='Create pnkln rapid drill: (1) Premortem top10+mitigations (2) Rollback rehearsal timed checklist with pass/fail gates (3) Failure injection plan (scope, guardrails, auto-revert) (4) Audit trail artifact list. Return owners,timings,pass/fail,one-paragraph debrief template.'

    echo "## 09_rapid_drill_exec"
    gen "$PROMPT"
}

# ==============================================================================
# 10_investor_slides_exec - Generate investor slides
# ==============================================================================
run_investor_slides() {
    local PROMPT='Produce 2-slide investor text. Slide1 Impact: throughput2×; safety+90%; decision2×; endurance2.2×; 3 proof bullets. Slide2 Dollars: startup +$3M/yr ARR-eq → +$30M@10×; mid+enterprise ranges; key assumptions; CTA.'

    echo "## 10_investor_slides_exec"
    gen "$PROMPT"
}

# ==============================================================================
# 11_per_file_exec - Apply SOPs per file
# ==============================================================================
run_per_file() {
    local FILES="${FILES:-triage.py:Upload Triage,release_pipeline.js:Change & Release,decision_log.md:Decision Protocol,review_checklist.md:Code Review}"

    echo "## 11_per_file_exec"
    IFS=',' read -ra PAIRS <<< "$FILES"
    for pair in "${PAIRS[@]}"; do
        local f="${pair%%:*}"
        local t="${pair#*:}"
        local PROMPT="Apply pnkln SOP to file: $f | Topic: $t | Enforce relevant SOP(s) | Return steps, checklist, expected artifacts | Keep objections per pnklnJR; apply ARM brakes."
        echo "### File: $f"
        gen "$PROMPT"
    done
}

# ==============================================================================
# 12_repo_master_macro_exec - Run master macro
# ==============================================================================
run_master_macro() {
    local PROMPT='Enforce full pnkln SOPs across scope: UploadTriage→tickets→ActiveResources→delta; Change&Release→premortem5→flag→drill→promote/rollback→postmortem<24h; DecisionProtocol→structured log; CodeReview→checklist pass. Return unified plan, diffs/actions, final executive summary.'

    echo "## 12_repo_master_macro_exec"
    gen "$PROMPT"
}

# ==============================================================================
# 13_strategy_position_specs_echo - Echo strategy
# ==============================================================================
echo_strategy() {
    echo "## 13_strategy_position_specs_echo"
    echo "Strategy: cognitive-ops engine compounding via SOP automation; Position: AI-augmented discipline(2× speed+safer); Specs: SOP-engine, Studio prompts, Workbench shells, All-Hands, RapidDrill, Valuation, AuditTrail."
}

# ==============================================================================
# 14_ocrsumm_echo - Echo OCR summary
# ==============================================================================
echo_ocr() {
    echo "## 14_ocrsumm_echo"
    echo "OCR: no images supplied in latest; pipeline ready—SOP-A triage on ingest; append summaries to ActiveResources."
}

# ==============================================================================
# 15_agent_router_echo - Agent task router
# ==============================================================================
route_agent() {
    local TASK="${TASK:-primer}"

    echo "## 15_agent_router_echo"
    case "$TASK" in
        primer)    echo "route:02_primer_exec" ;;
        all_hands) echo "route:04_all_hands_exec" ;;
        valuation) echo "route:07_valuation_exec" ;;
        rapid)     echo "route:09_rapid_drill_exec" ;;
        master)    echo "route:12_repo_master_macro_exec" ;;
        per_file)  echo "route:11_per_file_exec" ;;
        *)         echo "route:02_primer_exec" ;;
    esac
}

# ==============================================================================
# 16_healthcheck_echo - Healthcheck
# ==============================================================================
healthcheck() {
    echo "## 16_healthcheck_echo"
    echo "pnkln_ready:${GOOGLE_CLOUD_PROJECT:-unset}@${REGION:-us-central1} model:${MODEL:-gemini-1.5-pro}"
}

# ==============================================================================
# Run all sections
# ==============================================================================
run_all() {
    init_env
    enable_services
    run_primer
    run_repo_enforcement
    run_all_hands
    echo_sops
    echo_frameworks
    run_valuation_ai
    calc_valuation_numbers
    run_rapid_drill
    run_investor_slides
    run_per_file
    run_master_macro
    echo_strategy
    echo_ocr
    route_agent
    healthcheck
}

# ==============================================================================
# Help
# ==============================================================================
show_help() {
    head -n 30 "$0" | tail -n 28
}

# ==============================================================================
# Main
# ==============================================================================
main() {
    local cmd="${1:-help}"

    case "$cmd" in
        all)       init_env && run_all ;;
        init)      init_env && enable_services ;;
        primer)    init_env && run_primer ;;
        repo)      init_env && run_repo_enforcement ;;
        allhands)  init_env && run_all_hands ;;
        sops)      echo_sops && echo_frameworks ;;
        valuation) init_env && run_valuation_ai && calc_valuation_numbers ;;
        drill)     init_env && run_rapid_drill ;;
        investor)  init_env && run_investor_slides ;;
        perfile)   init_env && run_per_file ;;
        master)    init_env && run_master_macro ;;
        status)    echo_strategy && echo_ocr ;;
        route)     route_agent ;;
        health)    healthcheck ;;
        help|--help|-h) show_help ;;
        *)         echo "Unknown command: $cmd"; show_help; exit 1 ;;
    esac
}

main "$@"

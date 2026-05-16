0 ENV

```bash
%%bash
set -euo pipefail
export PROJECT_ID="YOUR_GCP_PROJECT_ID"
export LOCATION="us-central1"
export PNKLN_BUCKET="gs://pnkln-$(date +%Y%m%d)-$RANDOM"
export PNKLN_DATASET="pnkln_ops"
export PNKLN_OUT="/tmp/pnkln_out"
export PNKLN_LEDGER="/tmp/pnkln_ledgers"
mkdir -p "${PNKLN_OUT}" "${PNKLN_LEDGER}"
gcloud services enable aiplatform.googleapis.com storage.googleapis.com bigquery.googleapis.com --project="${PROJECT_ID}"
gsutil mb -p "${PROJECT_ID}" -l "${LOCATION}" -b on "${PNKLN_BUCKET}" || true
bq --project_id="${PROJECT_ID}" --location="${LOCATION}" mk -f "${PNKLN_DATASET}" || true
printf "%s\n" "${PNKLN_BUCKET} ${PROJECT_ID}.${PNKLN_DATASET} ${LOCATION}"
```

1 DOCS_INVESTOR

```bash
%%bash
set -euo pipefail
cat > /tmp/pnkln_investor_one_slide.md <<'MD'
# pnkln — Investor One-Slide
What: governed AI DevOps (IDE→CI→graph→runtime) as policy-as-code with receipts.
Now: +22–40% eng payroll; ~25% GPU/encode if material; 10-dev (~$2.2M): $0.49–$0.88M/yr.
Price: $60–$120k ARR / 10-dev (8–12× ROI).
Moat: enforceable loop + ledgers.
Future: ads/QoE + infra + enterprise + marketplace → $100–200M+ path.
MD
gsutil cp /tmp/pnkln_investor_one_slide.md "${PNKLN_BUCKET}/docs/"
printf "%s\n" "${PNKLN_BUCKET}/docs/pnkln_investor_one_slide.md"
```

2 DOCS_BOARD

```bash
%%bash
set -euo pipefail
cat > /tmp/pnkln_board_brief.md <<'MD'
# pnkln — Board Brief
Track: CPM +5–15%, QoE minutes +3–6%, COGS/hr −10–20%, Eng +22–40%.
Next: (1) attach provenance+perf receipts per session; (2) policy ledger + exec dashboard.
MD
gsutil cp /tmp/pnkln_board_brief.md "${PNKLN_BUCKET}/docs/"
printf "%s\n" "${PNKLN_BUCKET}/docs/pnkln_board_brief.md"
```

3 STUDIO_PROMPTS

```bash
%%bash
set -euo pipefail
cat > /tmp/pnkln_prompt_pack_studio.md <<'MD'
# pnkln — Studio Prompt Pack
A) Co-founder (governed): System: policy-as-code; staged-first; minimal diffs; Two-Greens (concept); receipts-or-fail-closed. User: Context {{context}} → 7-bullet exec; ≤7 risks; ≤7 pre-mortem; 5-Whys(top); objections; 3 next steps.
B) QoE Pre-mortem: System: pnkln playback red-team. User: 10 QoE failures with detection/mitigation/owner/minutes&CPM impact.
C) Minimal-diff rewrite: System: clarity editor. User: single-idea; metrics-first; no hedging; ≤120 words. Text {{block}}.
D) Test plan: System: decision-driving tests. User: hypothesis/steps/expected signal(QoE|CPM)/owner/go-no-go. Spec {{spec}}.
E) Receipts summary: System: board voice. User: 5 bullets for provenance/QoE/CPM/COGS + 1 kill-metric. Inputs {{receipts}}.
F) Pricing & ROI: System: conservative estimator. User: team_size {{n_devs}}, payroll_per_dev {{payroll}}, gpu_spend {{gpu}} → 22–40% payroll now-savings, ~25% GPU, price for 8–12× ROI.
MD
gsutil cp /tmp/pnkln_prompt_pack_studio.md "${PNKLN_BUCKET}/studio/"
printf "%s\n" "${PNKLN_BUCKET}/studio/pnkln_prompt_pack_studio.md"
```

4 FIN_NOW_CSV

```bash
%%bash
set -euo pipefail
cat > /tmp/pnkln_now_value_by_team.csv <<'CSV'
team_size,baseline_payroll_usd,conservative_22pct,aggressive_40pct
1,220000,48400,88000
5,1100000,242000,440000
10,2200000,484000,880000
25,5500000,1210000,2200000
CSV
gsutil cp /tmp/pnkln_now_value_by_team.csv "${PNKLN_BUCKET}/finance/"
printf "%s\n" "${PNKLN_BUCKET}/finance/pnkln_now_value_by_team.csv"
```

5 LEDGER_PROVENANCE

```bash
%%bash
set -euo pipefail
ASSET="${PNKLN_OUT}/example_asset.txt"; printf "pnkln %s\n" "$(date -u +%FT%TZ)" > "${ASSET}"
SHA256=$(openssl dgst -sha256 "${ASSET}" | awk '{print $2}')
STAMP=$(date -u +%FT%TZ)
SIZE=$(wc -c < "${ASSET}")
OBJ="${PNKLN_BUCKET}/assets/example_asset.txt"
gsutil cp "${ASSET}" "${OBJ}"
gsutil setmeta -h "x-goog-meta-sha256:${SHA256}" -h "x-goog-meta-stamped:${STAMP}" "${OBJ}"
LEDGER="${PNKLN_LEDGER}/provenance_ledger.csv"
[[ -f "${LEDGER}" ]] || echo "timestamp,object_path,sha256,size_bytes,user" > "${LEDGER}"
echo "${STAMP},${OBJ},${SHA256},${SIZE},${USER:-vertex}" >> "${LEDGER}"
gsutil cp "${LEDGER}" "${PNKLN_BUCKET}/ledgers/provenance_ledger.csv"
bq query --use_legacy_sql=false --project_id="${PROJECT_ID}" --location="${LOCATION}" "CREATE TABLE IF NOT EXISTS \`${PROJECT_ID}.${PNKLN_DATASET}.provenance_ledger\`(timestamp TIMESTAMP,object_path STRING,sha256 STRING,size_bytes INT64,user STRING)"
bq load --source_format=CSV --autodetect --replace=false --project_id="${PROJECT_ID}" --location="${LOCATION}" "${PNKLN_DATASET}.provenance_ledger" "${PNKLN_BUCKET}/ledgers/provenance_ledger.csv"
printf "%s\n" "${OBJ}"
```

6 LEDGER_POLICY

```bash
%%bash
set -euo pipefail
bq query --use_legacy_sql=false --project_id="${PROJECT_ID}" --location="${LOCATION}" "CREATE TABLE IF NOT EXISTS \`${PROJECT_ID}.${PNKLN_DATASET}.policy_ledger\`(stamped TIMESTAMP,policy STRING,subject STRING,domain STRING,outcome STRING,receipts STRING)"
cat > /tmp/pnkln_policy_ledger_row.csv <<'CSV'
stamped,policy,subject,domain,outcome,receipts
2025-10-25T00:00:00Z,codegraph_freshness,search_index,pnkln,pass,"{""scip"":true,""coverage"":0.98}"
CSV
gsutil cp /tmp/pnkln_policy_ledger_row.csv "${PNKLN_BUCKET}/ledgers/"
bq load --source_format=CSV --autodetect --replace=false --project_id="${PROJECT_ID}" --location="${LOCATION}" "${PNKLN_DATASET}.policy_ledger" "${PNKLN_BUCKET}/ledgers/pnkln_policy_ledger_row.csv"
printf "%s\n" "${PNKLN_BUCKET}/ledgers/pnkln_policy_ledger_row.csv"
```

7 TRANSFER_PACK

```bash
%%bash
set -euo pipefail
cat > /tmp/pnkln_master_transfer_list.csv <<'CSV'
filename,description
pnkln_thread_summary.md,Thread latest summary
pnkln_investor_one_slide.md,Investor cut
pnkln_board_brief.md,Board cut
pnkln_prompt_pack_studio.md,Studio prompts
pnkln_now_value_by_team.csv,Now-value CSV
pnkln_master_transfer_list.csv,This list
pnkln_master_transfer_manifest.json,Manifest
pnkln_master_transfer_instructions.md,Transfer how-to
CSV
cat > /tmp/pnkln_master_transfer_manifest.json <<'JSON'
{"version":"1.0","name":"pnkln_thread_rollup","files":[
{"filename":"pnkln_thread_summary.md","description":"Thread latest summary"},
{"filename":"pnkln_investor_one_slide.md","description":"Investor cut"},
{"filename":"pnkln_board_brief.md","description":"Board cut"},
{"filename":"pnkln_prompt_pack_studio.md","description":"Studio prompts"},
{"filename":"pnkln_now_value_by_team.csv","description":"Now-value CSV"},
{"filename":"pnkln_master_transfer_list.csv","description":"This list"},
{"filename":"pnkln_master_transfer_manifest.json","description":"Manifest"},
{"filename":"pnkln_master_transfer_instructions.md","description":"Transfer how-to"}]}
JSON
cat > /tmp/pnkln_master_transfer_instructions.md <<'MD'
# pnkln Transfer
1) Download from GCS; 2) Upload in new thread or keep GCS; 3) Start with pnkln_thread_summary.md; re-hash and append ledgers after move.
MD
gsutil cp /tmp/pnkln_master_transfer_list.csv "${PNKLN_BUCKET}/transfer/"
gsutil cp /tmp/pnkln_master_transfer_manifest.json "${PNKLN_BUCKET}/transfer/"
gsutil cp /tmp/pnkln_master_transfer_instructions.md "${PNKLN_BUCKET}/transfer/"
printf "%s\n" "${PNKLN_BUCKET}/transfer/"
```

8 THREAD_SUMMARY

```bash
%%bash
set -euo pipefail
cat > /tmp/pnkln_thread_summary.md <<'MD'
# pnkln — Thread Summary (Latest Only)
Enforceable DevOps spine with receipts; Now: 22–40% payroll; ~25% GPU if applicable; Price $60–$120k / 10-dev; Future: ads/QoE + infra + enterprise + marketplace → $100–200M+; Included: investor, board, prompts, now-value CSV, ledgers, transfer pack; Skip git.
MD
gsutil cp /tmp/pnkln_thread_summary.md "${PNKLN_BUCKET}/docs/"
printf "%s\n" "${PNKLN_BUCKET}/docs/pnkln_thread_summary.md"
```

9 ZIP_ROLLUP

```bash
%%bash
set -euo pipefail
cp /tmp/pnkln_investor_one_slide.md "${PNKLN_OUT}/"
cp /tmp/pnkln_board_brief.md "${PNKLN_OUT}/"
cp /tmp/pnkln_prompt_pack_studio.md "${PNKLN_OUT}/"
cp /tmp/pnkln_now_value_by_team.csv "${PNKLN_OUT}/"
cp /tmp/pnkln_master_transfer_list.csv "${PNKLN_OUT}/"
cp /tmp/pnkln_master_transfer_manifest.json "${PNKLN_OUT}/"
cp /tmp/pnkln_master_transfer_instructions.md "${PNKLN_OUT}/"
cp /tmp/pnkln_thread_summary.md "${PNKLN_OUT}/"
cd "${PNKLN_OUT}"
zip -q pnkln_thread_rollup.zip pnkln_*
gsutil cp pnkln_thread_rollup.zip "${PNKLN_BUCKET}/rollups/"
gsutil ls -r "${PNKLN_BUCKET}/" | sed -n '1,40p'
```

10 OCR_STUB

```bash
%%bash
set -euo pipefail
printf "%s\n" "No images in thread; add URIs and wire DocAI/Vision if needed."
```

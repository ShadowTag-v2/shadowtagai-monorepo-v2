def add_import_os(filepath):
    with open(filepath) as f:
        content = f.read()
    if "import os" not in content:
        content = "import os\n" + content
        with open(filepath, "w") as f:
            f.write(content)


files_to_fix = [
    "apps/aiyou_stack/aiyou-fastapi-services/services/innovation_lab/main.py",
    "apps/aiyou_stack/aiyou-fastapi-services/services/platform-monitoring/api.py",
    "apps/aiyou_stack/aiyou-fastapi-services/services/v2x-mesh/api.py",
    "apps/aiyou_stack/aiyou-fastapi-services/shadowtag/api.py",
    "apps/aiyou_stack/aiyou-fastapi-services/src/api/consolidated_api.py",
    "apps/aiyou_stack/aiyou-fastapi-services/src/main.py",
]

for fp in files_to_fix:
    add_import_os(fp)

# Fix SIM102
fp2 = "apps/aiyou_stack/aiyou-fastapi-services/src/Claude_Code_6/judge_core.py"
with open(fp2) as f:
    content = f.read()
content = content.replace(
    '        if "cloud" in action.lower() or "cluster" in action.lower():\n            if not context.get("infra_approved"):',
    '        if ("cloud" in action.lower() or "cluster" in action.lower()) and not context.get("infra_approved"):',
)
with open(fp2, "w") as f:
    f.write(content)

# Fix B904
fp3 = "apps/aiyou_stack/aiyou-fastapi-services/src/ingestion-layer/ingestion_orchestrator.py"
with open(fp3) as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "raise SystemExit(2)" in line:
        lines[i] = line.replace("raise SystemExit(2)", "raise SystemExit(2) from e")
with open(fp3, "w") as f:
    f.writelines(lines)

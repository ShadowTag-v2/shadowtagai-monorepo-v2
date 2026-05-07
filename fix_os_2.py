files = [
    "apps/aiyou_stack/aiyou-fastapi-services/corp_engine/api/main.py",
    "apps/aiyou_stack/aiyou-fastapi-services/services/innovation_lab/main.py",
    "apps/aiyou_stack/aiyou-fastapi-services/services/platform-monitoring/api.py",
    "apps/aiyou_stack/aiyou-fastapi-services/services/v2x-mesh/api.py",
    "apps/aiyou_stack/aiyou-fastapi-services/shadowtag/api.py",
    "apps/aiyou_stack/aiyou-fastapi-services/src/api/consolidated_api.py",
    "apps/aiyou_stack/aiyou-fastapi-services/src/main.py",
]

for f in files:
    with open(f) as file:
        content = file.read()
    with open(f, "w") as file:
        file.write("import os\n" + content)

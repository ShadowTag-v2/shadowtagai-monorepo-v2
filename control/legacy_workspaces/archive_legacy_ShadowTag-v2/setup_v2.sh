# setup_v2.sh
mkdir -p apps/flyingmonkeys-server/src \
         libs/aiyou/{agents,governance,proxies,connectors} \
         libs/arsenal/{shadowtag_core,jetski,scribe} \
         infra/{terraform,docker/cockpit} \
         .agent/{rules,workflows,context} .beads/
echo ">>> ✅ Scaffolding Complete."

# setup_v2.sh
mkdir -p apps/n-autoresearch/Kosmos/BioAgents-server/src \
         libs/ShadowTag-v2/{agents,governance,proxies,connectors} \
         libs/arsenal/{shadowtag_core,jetski,scribe} \
         infra/{terraform,docker/cockpit} \
         .agent/{rules,workflows,context} .beads/
echo ">>> ✅ Scaffolding Complete."

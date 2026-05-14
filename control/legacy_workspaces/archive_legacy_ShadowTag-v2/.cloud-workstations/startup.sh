#!/bin/bash
# .cloud-workstations/startup.sh

echo ">>> 🚀 INITIATING ANTIGRAVITY IGNITION..."

# 1. Authenticate Docker for AlloyDB
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# 2. Wake the Hippocampus (AlloyDB Omni)
if [ ! "$(docker ps -q -f name=antigravity-db)" ]; then
    echo ">>> 🧠 Waking up AlloyDB..."
    docker run --rm -d --name antigravity-db \
        -p 5432:5432 \
        -e POSTGRES_PASSWORD=antigravity \
        -v /home/user/antigravity-data:/var/lib/postgresql/data \
        google/alloydb-omni \
        postgres -c "shared_preload_libraries=vector,google_ml_integration"
fi

# 3. Hydrate Knowledge Base
cd /home/user/ShadowTag-v2 && git pull origin main

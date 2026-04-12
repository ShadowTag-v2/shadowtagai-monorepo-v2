
FROM python:3.11-slim

# Install git and system deps
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Dependencies FIRST (Cache layer)
RUN pip install kafka-python google-cloud-storage google-cloud-logging

# Metadata
ENV PROJECT_ID="shadowtag-omega-v2"
ENV PYTHONUNBUFFERED=1

# COPY ONLY SCRIPTS (Lightweight)
COPY scripts/ /app/scripts/

# PIVOT: Do NOT copy the whole repo.
# We will clone it at runtime or expect a mounted volume.
# For simplicity in this "Trojan Horse" v2:
# We will assume the user has a repo URL we can clone, providing the data freshness.
# OR we simply accept that we only scan what we can fetch.
# But wait, the user's "347 branches" might only exist locally or on their specific remote.
# If they are on 'origin' (GitHub), we can clone.
# Let's try to clone the public repo if possible, or fail fast and ask for auth.
# Actually, better pattern:
# The `scripts/harvest_docs_producer.py` will now include a `git clone` step if the dir is empty.

CMD ["python3", "scripts/harvest_docs_producer.py"]

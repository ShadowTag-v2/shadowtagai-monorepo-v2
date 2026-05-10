# Antigravity on Cloud Workstation (Chrome Remote Desktop)

**Objective:** Provision a persistent, browser-accessible Antigravity IDE environment.
**Status:** Validated Jan 2026.

## 1. Dockerfile (Custom Image)

```dockerfile
FROM us-central1-docker.pkg.dev/cloud-workstations-images/predefined/base
ARG DEBIAN_FRONTEND=noninteractive

# Install desktop (XFCE) + deps
RUN apt-get update && apt-get install -y \
    xvfb xfce4 xfce4-goodies xbase-clients dbus-x11 psmisc python3-psutil xserver-xorg-video-dummy \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Chrome + Chrome Remote Desktop
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list > /dev/null && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] https://dl.google.com/linux/chrome-remote-desktop/deb stable main" | tee /etc/apt/sources.list.d/chrome-remote-desktop.list > /dev/null && \
    apt-get update && \
    apt-get install -y google-chrome-stable chrome-remote-desktop && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Chrome sandbox fix (container-safe)
RUN dpkg-divert --add --rename --divert /usr/bin/google-chrome-stable.real /usr/bin/google-chrome-stable && \
    echo '#!/bin/bash' > /usr/bin/google-chrome-stable && \
    echo 'exec /usr/bin/google-chrome-stable.real --no-sandbox --disable-dev-shm-usage "$@"' >> /usr/bin/google-chrome-stable && \
    chmod +x /usr/bin/google-chrome-stable

# Mock systemctl (container compat)
RUN echo '#!/bin/bash' > /usr/bin/systemctl && \
    echo 'echo "Mock systemctl: $@"' >> /usr/bin/systemctl && \
    echo 'exit 0' >> /usr/bin/systemctl && \
    chmod +x /usr/bin/systemctl

# Install Antigravity (official repo)
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://us-central1-apt.pkg.dev/doc/repo-signing-key.gpg | gpg --dearmor -o /etc/apt/keyrings/antigravity-repo-key.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/antigravity-repo-key.gpg] https://us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev/ antigravity-debian main" | tee /etc/apt/sources.list.d/antigravity.list > /dev/null && \
    apt-get update && \
    apt-get install -y antigravity && \
    dpkg-divert --add --rename --divert /usr/bin/antigravity.real /usr/bin/antigravity && \
    echo '#!/bin/bash' > /usr/bin/antigravity && \
    echo 'exec /usr/bin/antigravity.real --no-sandbox --disable-dev-shm-usage --disable-gpu "$@"' >> /usr/bin/antigravity && \
    chmod +x /usr/bin/antigravity

# Copy startup scripts (create dir first)
COPY startup-scripts/ /etc/workstation-startup.d/
RUN chmod +x /etc/workstation-startup.d/*
```

## 2. Startup Script (100-setup-cr.sh)

See artifact: `src/antigravity/workstations/startup.sh`

## 3. Provisioning Commands

```bash
# Build
gcloud builds submit --region=us-central1 \
  --tag us-central1-docker.pkg.dev/shadowtag-omega-v2/repo/antigravity:latest

# Create Cluster
gcloud workstations clusters create ws-cluster --region=us-central1

# Create Config
gcloud workstations configs create antigravity-config \
  --cluster=ws-cluster --region=us-central1 \
  --machine-type=e2-standard-8 --boot-disk-size=200 \
  --container-custom-image=us-central1-docker.pkg.dev/shadowtag-omega-v2/repo/antigravity:latest \
  --shielded-integrity-monitoring --shielded-secure-boot --shielded-vtpm

# Create Workstation
gcloud workstations create my-antigravity --cluster=ws-cluster \
  --config=antigravity-config --region=us-central1 \
  --start-async
```

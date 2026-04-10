
# ANTIGRAVITY ON CLOUD WORKSTATIONS: SETUP GUIDE

**Goal**: Run Antigravity (VS Code Fork) on a Google Cloud Workstation with a full GUI via Chrome Remote Desktop, bypassing local firewall/policy restrictions.

## 1. Prerequisites
*   Google Cloud Project with Billing enabled.
*   Permissions: `roles/workstations.admin`, `roles/compute.admin`, `roles/iam.serviceAccountUser`.
*   APIs Enabled: `workstations.googleapis.com`, `compute.googleapis.com`, `cloudbuild.googleapis.com`.

## 2. Dockerfile Configuration
Create a `Dockerfile` that installs XFCE, Chrome, Chrome Remote Desktop, and Antigravity.

```dockerfile
FROM us-central1-docker.pkg.dev/cloud-workstations-images/predefined/base
ARG DEBIAN_FRONTEND=noninteractive

# 1. Install Desktop Env (XFCE) & Deps
RUN apt-get update && apt-get install -y \
    xvfb xfce4 xfce4-goodies xbase-clients dbus-x11 psmisc python3-psutil xserver-xorg-video-dummy \
    && apt-get clean

# 2. Install Chrome & Remote Desktop
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list > /dev/null && \
    apt-get update && apt-get install -y google-chrome-stable chrome-remote-desktop

# 3. Chrome Sandbox Fix (Critical for Container)
RUN dpkg-divert --add --rename --divert /usr/bin/google-chrome-stable.real /usr/bin/google-chrome-stable && \
    echo '#!/bin/bash' > /usr/bin/google-chrome-stable && \
    echo 'exec /usr/bin/google-chrome-stable.real --no-sandbox --disable-dev-shm-usage "$@"' >> /usr/bin/google-chrome-stable && \
    chmod +x /usr/bin/google-chrome-stable

# 4. Install Antigravity (Mocked for public steps - Replace with actual Antigravity install if available)
# If using actual Antigravity deb:
# COPY antigravity.deb /tmp/
# RUN apt-get install -y /tmp/antigravity.deb

# 5. Startup Script
COPY startup.sh /etc/workstation-startup.d/
RUN chmod +x /etc/workstation-startup.d/startup.sh
```

## 3. Startup Script (`startup.sh`)
Ensures Chrome Remote Desktop starts on boot.

```bash
#!/bin/bash
TARGET_USER="user"
HOME_DIR="/home/$TARGET_USER"

# Create Session File
if [ ! -f "$HOME_DIR/.chrome-remote-desktop-session" ]; then
    cat <<'EOF' > "$HOME_DIR/.chrome-remote-desktop-session"
#!/bin/bash
export DESKTOP_SESSION=xfce
export XDG_CURRENT_DESKTOP=XFCE
exec /usr/bin/dbus-launch --exit-with-session /usr/bin/startxfce4
EOF
    chown $TARGET_USER:$TARGET_USER "$HOME_DIR/.chrome-remote-desktop-session"
    chmod +x "$HOME_DIR/.chrome-remote-desktop-session"
fi

# Start Service
/opt/google/chrome-remote-desktop/chrome-remote-desktop --start
```

## 4. Build & Deploy
1.  **Build Image**:
    ```bash
    gcloud builds submit --tag gcr.io/$PROJECT_ID/antigravity-ws:latest .
    ```
2.  **Create Workstation Config**:
    ```bash
    gcloud workstations configs create antigravity-config \
        --cluster=my-cluster \
        --region=us-central1 \
        --container-custom-image=gcr.io/$PROJECT_ID/antigravity-ws:latest \
        --machine-type=e2-standard-8
    ```
3.  **Create Workstation**:
    ```bash
    gcloud workstations create my-ws --config=antigravity-config ...
    ```

## 5. Connect (The "Headless" Trick)
1.  Go to [remotedesktop.google.com/headless](https://remotedesktop.google.com/headless).
2.  Click "Begin", "Next", "Authorize".
3.  Copy the **Debian Linux** command (looks like `DISPLAY= /opt/... --code="4/..."`).
4.  SSH into your workstation:
    ```bash
    gcloud workstations ssh my-ws
    ```
5.  Paste the command. Set a PIN.
6.  Go to [remotedesktop.google.com/access](https://remotedesktop.google.com/access), click your workstation, enter PIN.
7.  **Success**: You now have a full Linux GUI in your browser. Open terminal, run `antigravity`.

## 6. Removing Limitations (Cloud Admin)
Since you are root/admin on this Cloud Workstation:
*   **Browsers**: You can launch Chrome/Firefox without "Workspace Trust" blocks (add `--no-sandbox`).
*   **Extensions**: Install any VS Code extension.
*   **Persistence**: Your home directory (`/home/user`) persists across reboots if configured with a persistent disk.

> **Note**: Specific internal "Antigravity" policies (like proprietary extension blocks) are baked into the binary. To bypass those, you'd need to modify the binary or use the Open Source VS Code Server instead, but then you lose the specific Antigravity agents.

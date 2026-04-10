
# CRD OPTIMIZATION PLAN (UPHILL SNOWBALL)

**Source**: `libs/external/cloud-workstations-examples/examples/gnome-crd/Dockerfile`
**Analysis Date**: 2026-01-27
**Purpose**: Harden the Sovereign Node (`uphillsnowball`) using Google's best practices.

## 1. Core Improvements
Based on the `gnome-crd` example, we can optimize our remote desktop setup:

- **Systemd Integration**: Use proper systemd units (`chrome-remote-desktop@user.service`) instead of manual start scripts.
- **Audio Handling**: Explicitly disable `pulseaudio` via systemd masking to prevent conflicts with CRD's internal audio handling.
- **Polkit Suppression**: Use `.pkla` overrides (`10-chrome-remote-desktop.pkla`) to stop annoying authentication popups in the remote session.
- **Chrome Optimization**: Launch Chrome with `--disable-dev-shm-usage` to prevent crashes in containerized environments.

## 2. Infrastructure Upgrade Steps
1.  **Container Build**: Refactor the `uphillsnowball` Dockerfile to incorporate the `files/` assets from the example (polkit, systemd services).
2.  **Startup Script**: Replace ad-hoc `entrypoint.sh` with the robust `prepare-environment.sh` logic.
3.  **User Management**: Automate user creation and group assignment (`chrome-remote-desktop` group).

## 3. Security Implications
- **Reduced Attack Surface**: Disabling unused services (like `ssh` if managed by workstation startup) reduces vectors.
- **Stability**: Proper systemd integration prevents "zombie" sessions and improves restart reliability.

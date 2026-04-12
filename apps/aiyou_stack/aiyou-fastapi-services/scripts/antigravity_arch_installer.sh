#!/bin/bash
# =============================================================================
# Google Antigravity Arch Linux Installer
# Based on Technical Audit for asychin/antigravity-arch
#
# Addresses three failure domains:
# 1. Security Compliance (Chromium SUID sandbox)
# 2. Kernel Resource Negotiation (inotify limits)
# 3. Hardware Compatibility (AVX2 requirement)
# =============================================================================

set -euo pipefail

VERSION="1.0.0"
INSTALL_DIR="/opt/antigravity"
DOWNLOAD_URL="https://edgedl.me.gvt1.com/edgedl/chrome/dict/antigravity-stable-latest.tar.gz"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# =============================================================================
# PRE-FLIGHT CHECKS
# =============================================================================

check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_warn "Running as root. Some operations will use sudo anyway for clarity."
    fi
}

check_avx2() {
    log_info "Checking AVX2 support..."
    if ! grep -q avx2 /proc/cpuinfo 2>/dev/null; then
        log_error "FATAL: Your CPU does not support AVX2 instructions."
        log_error "Google Antigravity requires AVX2 to function."
        log_error ""
        log_error "If running in a VM (Proxmox/KVM), change CPU type to 'host'"
        log_error "to pass through the host CPU instruction sets."
        exit 1
    fi
    log_info "AVX2 support: OK"
}

check_inotify() {
    log_info "Checking inotify limits..."
    local current
    current=$(cat /proc/sys/fs/inotify/max_user_watches)
    local required=524288

    if [ "$current" -lt "$required" ]; then
        log_warn "inotify watches too low: $current (need $required)"
        log_info "Applying fix..."

        # Immediate fix
        sudo sysctl -w fs.inotify.max_user_watches=$required

        # Permanent fix
        echo "fs.inotify.max_user_watches=$required" | sudo tee /etc/sysctl.d/40-antigravity-watches.conf

        log_info "inotify limit increased to $required"
    else
        log_info "inotify watches: OK ($current)"
    fi
}

check_dependencies() {
    log_info "Checking dependencies..."
    local deps=(nss gtk3 alsa-lib libxss libxtst at-spi2-core mesa xdg-utils)
    local missing=()

    for dep in "${deps[@]}"; do
        if ! pacman -Q "$dep" &>/dev/null; then
            missing+=("$dep")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        log_warn "Missing dependencies: ${missing[*]}"
        log_info "Installing missing dependencies..."
        sudo pacman -S --noconfirm "${missing[@]}"
    fi

    log_info "Dependencies: OK"
}

check_userns() {
    log_info "Checking user namespace support..."
    local userns
    userns=$(cat /proc/sys/kernel/unprivileged_userns_clone 2>/dev/null || echo "1")

    if [ "$userns" = "0" ]; then
        log_warn "Unprivileged user namespaces are DISABLED."
        log_warn "The Chromium sandbox may fail to launch."
        log_warn "Consider: sudo sysctl -w kernel.unprivileged_userns_clone=1"
    else
        log_info "User namespaces: OK"
    fi
}

# =============================================================================
# INSTALLATION
# =============================================================================

download_and_extract() {
    log_info "Downloading Antigravity..."

    local tmp_dir
    tmp_dir=$(mktemp -d)
    local tarball="$tmp_dir/antigravity.tar.gz"

    # Download with redirect following
    curl -L -o "$tarball" "$DOWNLOAD_URL" || {
        log_error "Download failed. Check your internet connection."
        exit 1
    }

    # TODO: Add SHA256 verification here
    # Expected: compare against known hash

    log_info "Extracting to $INSTALL_DIR..."

    # Remove old installation
    if [ -d "$INSTALL_DIR" ]; then
        log_warn "Removing existing installation..."
        sudo rm -rf "$INSTALL_DIR"
    fi

    sudo mkdir -p "$INSTALL_DIR"
    sudo tar -xzf "$tarball" -C "$INSTALL_DIR" --strip-components=1

    # Cleanup
    rm -rf "$tmp_dir"

    log_info "Extraction complete"
}

# =============================================================================
# CRITICAL: SUID SANDBOX FIX
# =============================================================================

fix_sandbox() {
    log_info "Applying SUID sandbox fix (CRITICAL)..."

    local sandbox="$INSTALL_DIR/chrome-sandbox"

    if [ ! -f "$sandbox" ]; then
        log_error "chrome-sandbox not found at $sandbox"
        log_error "Installation may be corrupted."
        exit 1
    fi

    # Set ownership to root
    sudo chown root:root "$sandbox"

    # Set SUID bit (4755)
    # 4 = SUID bit (allows privilege escalation for namespace creation)
    # 7 = owner rwx
    # 5 = group rx
    # 5 = others rx
    sudo chmod 4755 "$sandbox"

    # Verify
    local perms
    perms=$(stat -c "%a" "$sandbox")
    if [ "$perms" = "4755" ]; then
        log_info "Sandbox permissions: OK (4755 SUID)"
    else
        log_error "Failed to set sandbox permissions. Got: $perms"
        exit 1
    fi
}

# =============================================================================
# DESKTOP INTEGRATION
# =============================================================================

create_wrapper() {
    log_info "Creating launcher wrapper..."

    # Create wrapper script that forwards arguments
    cat << 'WRAPPER' | sudo tee /usr/bin/antigravity > /dev/null
#!/bin/bash
# Antigravity launcher wrapper
# Disables core dumps to prevent disk fill on crash loops
ulimit -c 0
exec /opt/antigravity/antigravity "$@"
WRAPPER

    sudo chmod 755 /usr/bin/antigravity
    log_info "Wrapper created at /usr/bin/antigravity"
}

create_desktop_entry() {
    log_info "Creating desktop entry..."

    # Find icon (path may vary between versions)
    local icon_path
    icon_path=$(find "$INSTALL_DIR" -name "*.png" -path "*/resources/*" | head -1)

    if [ -n "$icon_path" ]; then
        sudo cp "$icon_path" /usr/share/pixmaps/antigravity.png
    fi

    cat << 'DESKTOP' | sudo tee /usr/share/applications/antigravity.desktop > /dev/null
[Desktop Entry]
Name=Google Antigravity
Comment=AI-Powered Development Environment (Gemini 3 Pro)
GenericName=Agentic IDE
Exec=/usr/bin/antigravity %F
Icon=antigravity
Type=Application
StartupNotify=true
StartupWMClass=Antigravity
Categories=Development;IDE;TextEditor;
MimeType=text/plain;inode/directory;application/x-antigravity-workspace;
Keywords=antigravity;gemini;ai;code;editor;development;
DESKTOP

    # Update desktop database
    sudo update-desktop-database /usr/share/applications/ 2>/dev/null || true

    log_info "Desktop entry created"
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    echo "=============================================="
    echo "  Google Antigravity Arch Linux Installer"
    echo "  Version: $VERSION"
    echo "=============================================="
    echo ""

    # Pre-flight checks
    check_root
    check_avx2
    check_inotify
    check_dependencies
    check_userns

    echo ""
    log_info "Pre-flight checks passed. Starting installation..."
    echo ""

    # Installation
    download_and_extract
    fix_sandbox
    create_wrapper
    create_desktop_entry

    echo ""
    echo "=============================================="
    log_info "Installation complete!"
    echo ""
    echo "  Launch: antigravity"
    echo "  Or find 'Google Antigravity' in your app menu"
    echo ""
    echo "  Troubleshooting:"
    echo "    - Crashes immediately? Check AVX2 support"
    echo "    - 'Server crashed'? Check inotify limits"
    echo "    - Sandbox errors? Re-run this installer"
    echo "=============================================="
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

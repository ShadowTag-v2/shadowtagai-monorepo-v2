#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# ANTIGRAVITY // MAC PERFORMANCE OPTIMIZER v2.0
# Target: Apple Silicon (M1/M2/M3/M4) + Intel Macs
# JR Engine: Max performance within stability gates
# ═══════════════════════════════════════════════════════════════════════════

set -e
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "═══════════════════════════════════════════════════════════════"
echo "  ▛///▞ ANTIGRAVITY :: MAC OPTIMIZER"
echo "  Maximum Performance | Bootstrap Mode | Zero Cost"
echo "═══════════════════════════════════════════════════════════════"
echo -e "${NC}"

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: SYSTEM INFO
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[1/8] DETECTING SYSTEM...${NC}"
CHIP=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "Unknown")
RAM=$(sysctl -n hw.memsize 2>/dev/null | awk '{print $1/1073741824 " GB"}' || echo "Unknown")
MACOS=$(sw_vers -productVersion 2>/dev/null || echo "Unknown")
echo "  Chip: $CHIP"
echo "  RAM: $RAM"
echo "  macOS: $MACOS"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: DISABLE RESOURCE HOGS
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[2/8] DISABLING RESOURCE HOGS...${NC}"

# Disable Spotlight indexing (massive CPU/disk savings)
echo "  → Disabling Spotlight indexing..."
sudo mdutil -a -i off 2>/dev/null || echo "    (Spotlight: requires sudo)"

# Disable Siri
echo "  → Disabling Siri..."
defaults write com.apple.assistant.support "Assistant Enabled" -bool false 2>/dev/null
defaults write com.apple.Siri StatusMenuVisible -bool false 2>/dev/null
defaults write com.apple.Siri UserHasDeclinedEnable -bool true 2>/dev/null

# Disable Dictation
echo "  → Disabling Dictation..."
defaults write com.apple.HIToolbox AppleDictationAutoEnable -int 0 2>/dev/null

echo -e "${GREEN}  ✓ Resource hogs disabled${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: UI PERFORMANCE (REDUCE ANIMATIONS)
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[3/8] OPTIMIZING UI PERFORMANCE...${NC}"

# Reduce motion/transparency
echo "  → Reducing transparency..."
defaults write com.apple.universalaccess reduceTransparency -bool true 2>/dev/null

# Speed up animations
echo "  → Speeding up animations..."
defaults write NSGlobalDomain NSWindowResizeTime -float 0.001 2>/dev/null
defaults write com.apple.dock autohide-time-modifier -float 0 2>/dev/null
defaults write com.apple.dock autohide-delay -float 0 2>/dev/null
defaults write com.apple.dock expose-animation-duration -float 0.1 2>/dev/null
defaults write com.apple.dock launchanim -bool false 2>/dev/null

# Disable window animations
echo "  → Disabling window animations..."
defaults write NSGlobalDomain NSAutomaticWindowAnimationsEnabled -bool false 2>/dev/null
defaults write -g QLPanelAnimationDuration -float 0 2>/dev/null

# Speed up Mission Control
echo "  → Speeding up Mission Control..."
defaults write com.apple.dock expose-animation-duration -float 0.1 2>/dev/null

# Disable smooth scrolling (snappier feel)
echo "  → Optimizing scrolling..."
defaults write -g NSScrollAnimationEnabled -bool false 2>/dev/null

# Faster key repeat
echo "  → Faster keyboard response..."
defaults write NSGlobalDomain KeyRepeat -int 1 2>/dev/null
defaults write NSGlobalDomain InitialKeyRepeat -int 10 2>/dev/null

echo -e "${GREEN}  ✓ UI optimized for speed${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: FINDER OPTIMIZATIONS
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[4/8] OPTIMIZING FINDER...${NC}"

# Disable animations
echo "  → Disabling Finder animations..."
defaults write com.apple.finder DisableAllAnimations -bool true 2>/dev/null

# Show all files (dev productivity)
echo "  → Showing hidden files..."
defaults write com.apple.finder AppleShowAllFiles -bool true 2>/dev/null

# Show path bar and status bar
defaults write com.apple.finder ShowPathbar -bool true 2>/dev/null
defaults write com.apple.finder ShowStatusBar -bool true 2>/dev/null

# List view by default (faster rendering)
defaults write com.apple.finder FXPreferredViewStyle -string "Nlsv" 2>/dev/null

# Disable .DS_Store on network/USB drives
echo "  → Disabling .DS_Store on external drives..."
defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true 2>/dev/null
defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true 2>/dev/null

# Don't show recent tags
defaults write com.apple.finder ShowRecentTags -bool false 2>/dev/null

echo -e "${GREEN}  ✓ Finder optimized${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: MEMORY & DISK
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[5/8] OPTIMIZING MEMORY & DISK...${NC}"

# Purge RAM cache
echo "  → Purging memory cache..."
sudo purge 2>/dev/null || echo "    (purge: requires sudo)"

# Clear system caches
echo "  → Clearing user caches..."
rm -rf ~/Library/Caches/* 2>/dev/null || true

# Clear logs (can grow huge)
echo "  → Clearing old logs..."
sudo rm -rf /private/var/log/asl/*.asl 2>/dev/null || true

# Disable sudden motion sensor (SSD optimization - Intel only)
echo "  → Disabling sudden motion sensor (for SSDs)..."
sudo pmset -a sms 0 2>/dev/null || true

# Enable TRIM (for third-party SSDs)
echo "  → Checking TRIM status..."
TRIM_STATUS=$(system_profiler SPSerialATADataType 2>/dev/null | grep "TRIM Support" | head -1 || echo "N/A")
echo "    TRIM: $TRIM_STATUS"

echo -e "${GREEN}  ✓ Memory & disk optimized${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: NETWORK OPTIMIZATIONS
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[6/8] OPTIMIZING NETWORK...${NC}"

# Disable IPv6 (if not needed - faster DNS)
echo "  → Note: IPv6 left enabled (required for many services)"

# Flush DNS cache
echo "  → Flushing DNS cache..."
sudo dscacheutil -flushcache 2>/dev/null || true
sudo killall -HUP mDNSResponder 2>/dev/null || true

# Optimize TCP settings
echo "  → Optimizing TCP settings..."
sudo sysctl -w net.inet.tcp.delayed_ack=0 2>/dev/null || true
sudo sysctl -w net.inet.tcp.mssdflt=1440 2>/dev/null || true

echo -e "${GREEN}  ✓ Network optimized${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7: POWER & THERMAL
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[7/8] OPTIMIZING POWER & THERMAL...${NC}"

# Check if on AC power, enable high-performance mode
echo "  → Configuring power settings..."
# Disable App Nap (keeps apps responsive)
defaults write NSGlobalDomain NSAppSleepDisabled -bool true 2>/dev/null

# Prevent sleep when on AC
sudo pmset -c sleep 0 2>/dev/null || true
sudo pmset -c disksleep 0 2>/dev/null || true

# Enable high-performance mode (Apple Silicon)
echo "  → Note: For max performance, plug in power adapter"

echo -e "${GREEN}  ✓ Power optimized${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8: DEVELOPER OPTIMIZATIONS
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[8/8] DEVELOPER OPTIMIZATIONS...${NC}"

# Disable Gatekeeper's quarantine (faster app launches)
echo "  → Speeding up app launches..."
defaults write com.apple.LaunchServices LSQuarantine -bool false 2>/dev/null

# Disable crash reporter
echo "  → Disabling crash reporter dialogs..."
defaults write com.apple.CrashReporter DialogType -string "none" 2>/dev/null

# Enable debug menu in App Store
defaults write com.apple.appstore ShowDebugMenu -bool true 2>/dev/null

# Expand save panel by default
defaults write NSGlobalDomain NSNavPanelExpandedStateForSaveMode -bool true 2>/dev/null

# Disable auto-correct (dev productivity)
echo "  → Disabling auto-correct..."
defaults write NSGlobalDomain NSAutomaticSpellingCorrectionEnabled -bool false 2>/dev/null
defaults write NSGlobalDomain NSAutomaticCapitalizationEnabled -bool false 2>/dev/null

echo -e "${GREEN}  ✓ Developer optimizations applied${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# RESTART AFFECTED SERVICES
# ─────────────────────────────────────────────────────────────────────────────
echo -e "${YELLOW}Restarting affected services...${NC}"
killall Finder 2>/dev/null || true
killall Dock 2>/dev/null || true
killall SystemUIServer 2>/dev/null || true

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ OPTIMIZATION COMPLETE${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  RECOMMENDATIONS:"
echo "  1. Restart for all changes to take effect"
echo "  2. Install Macs Fan Control for thermal management"
echo "  3. Use Activity Monitor to identify remaining hogs"
echo "  4. Disable unused Login Items (System Settings → General → Login Items)"
echo ""
echo "  TO REVERSE: Run with --restore flag (not implemented yet)"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# OPTIONAL: AGGRESSIVE MODE
# ─────────────────────────────────────────────────────────────────────────────
if [[ "$1" == "--aggressive" ]]; then
    echo -e "${RED}[AGGRESSIVE MODE] Additional optimizations...${NC}"

    # Disable Time Machine local snapshots
    sudo tmutil disablelocal 2>/dev/null || true

    # Disable hibernation (faster wake)
    sudo pmset -a hibernatemode 0 2>/dev/null || true
    sudo rm -f /var/vm/sleepimage 2>/dev/null || true

    # Disable swap (only if 16GB+ RAM)
    # WARNING: Can cause issues if RAM is exhausted
    # sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.dynamic_pager.plist 2>/dev/null || true

    echo -e "${GREEN}  ✓ Aggressive optimizations applied${NC}"
fi

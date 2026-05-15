# Antigravity Cleaner - Professional Usage Guide

## 📚 Complete Module Guide

### 📂 Profile Backup & Restore (Session Manager)
**Session Manager** is the core module for managing browser identities.

#### How to Backup
1. Select **Option [2]** (Session Manager) from the Main Menu.
2. Select **Option [1]** (Backup Browser Profile).
3. Choose a profile from the list. The tool automatically detects profiles from Chrome, Edge, Brave, and Opera and maps them to their Google emails.
4. Choose Backup Mode:
    *   **[1] Light Mode:** Backs up essential data only (Cookies, Login Data, Preferences). Speed: Instant. Size: ~20MB. Best for quick switches.
    *   **[2] Full Mode:** Backs up everything (Extensions, History, Cache, etc.). Speed: Slow. Size: 500MB+. Best for full migration.

#### How to Restore
1. Select **Option [3]** (Restore Profile) inside Session Manager.
2. Select a backup from the list (sorted by date).
3. The tool will automatically **close the browser** and inject the files.
    *   *Warning:* Restoring overwrites current data for that profile.

---

### 🌍 Google Region Change (Region Inspector)
This module helps you check and change your Google Play / YouTube Premium region.

**Steps:**
1. Select **Option [5]** (Region Inspector) from Main Menu.
2. **CRITICAL:** Run the **Pre-Check** first. It opens browserleaks.com to check for:
    *   **IP Leak:** Is your VPN real IP visible?
    *   **DNS Leak:** Are you using ISP DNS?
    *   **WebRTC:** Is your local IP exposed?
3. Once safe, select a profile to open the hidden Google Country Association page.

---

### 🚀 Network Optimizer
Fixes connection issues typically caused by censorship or broken proxy settings.

*   **Flush DNS:** Clears corrupted DNS cache.
*   **Reset Winsock:** Resets the Windows socket catalog to clean state.
*   **Reset TCP/IP:** Reinstalls TCP/IP protocol stack.
*   *Note:* Requires Administrator privileges.

---

### 🧹 System Cleaner
Cleans traces that might link multiple accounts or reveal your location history.
*   **Temp Files:** Standard Windows temp cleaning.
*   **IDE Cache:** Clears JetBrains/VSCode caches which often store large amounts of metadata.

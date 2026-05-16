# Gemini Code Assist Plugin for Antigravity (macOS)

This guide documents how to configure Antigravity as a first-class "Gemini Code Assist plugin target" within a macOS-only environment. By standardizing on the `antigravity-proxy` flow, we can effectively "install" the Gemini Code Assist plugin for Antigravity.

## 1. Conceptual Mapping

In VS Code or IntelliJ, "installing the Gemini Code Assist plugin" means installing an IDE extension that communicates with the Gemini backend using your organization's credentials.

Antigravity is different:


- Antigravity has Gemini integration built-in.


- You cannot "install" a traditional plugin.


- Instead, you **insert a local MITM proxy** between Antigravity and `generativelanguage.googleapis.com` and **swap Google's key for your org's Gemini API key**.

For Antigravity, "installing Gemini Code Assist" for your organization means:

> **Set up `antigravity-proxy` as a local MITM proxy, then always launch Antigravity through that proxy so all Gemini requests use your organization's Gemini Code Assist API key.**

---

## 2. Prerequisites

For each developer machine that will use Antigravity + Gemini Code Assist:



- **OS**: macOS 14+ (Sonoma or newer).


- **Software**:


  - Antigravity IDE installed in `/Applications/Antigravity.app`.


  - Homebrew installed.


  - Python 3.8+ available.


- **Credentials**: An organization Gemini Code Assist Standard or Enterprise API key (with appropriate billing and IAM setup).


- **Access**: Admin rights to trust the mitmproxy CA certificate.


- **Network**: Ability to reach `generativelanguage.googleapis.com` and run a local proxy on port 8080.

---

## 3. One-Time Setup: "Install Gemini Code Assist for Antigravity"

This section is the Antigravity equivalent of "Open Extensions → Search 'Gemini Code Assist' → Install".

### 3.1 Install mitmproxy and Python dependencies

```bash

# 1) Install mitmproxy via Homebrew

brew install mitmproxy

# 2) Install python-dotenv for environment variable management

pip3 install python-dotenv

```

### 3.2 Clone and configure `antigravity-proxy`

```bash

# 3) Clone the proxy repository

git clone https://github.com/elad12390/antigravity-proxy.git
cd antigravity-proxy

# 4) Create your environment file

cp .env.example .env

```

**Edit `.env`**:
Set your organization's Gemini key. This is the **single place** where you map Antigravity's built-in Gemini usage to your org's credentials.

```env
GEMINI_API_KEY=your_org_gemini_code_assist_key_here
PROXY_PORT=8080   # Keep default unless necessary

```

### 3.3 Generate and trust the mitmproxy certificate

```bash

# 5) Generate certificates (runs mitmproxy once)

mitmproxy

# Wait for the UI to load, then press 'q' to quit.

```

The certificate is created at `~/.mitmproxy/mitmproxy-ca-cert.pem`.

**Trusting the Certificate on macOS**:



1. Open the certificate:
   ```bash
   open ~/.mitmproxy/mitmproxy-ca-cert.pem
   ```


2. In **Keychain Access**:


   - Locate the `mitmproxy` certificate (usually in the 'login' keychain).


   - Double-click it.


   - Expand the **Trust** section.


   - Set **"When using this certificate"** to **"Always Trust"**.


   - Close the window and enter your password to confirm.

> **Critical**: This step allows Antigravity to connect through the proxy over HTTPS without TLS errors.

---

## 4. Daily Use: Launch Antigravity "with Gemini Code Assist"

This is the equivalent of "Gemini Code Assist is ready for use".

### 4.1 Start the proxy

Open a terminal window, navigate to the proxy directory, and start it:

```bash
cd ~/path/to/antigravity-proxy

# Interactive mode (TUI)

mitmproxy -s mitmproxy-addon.py --listen-port 8080

```

*Keep this terminal window open.*

### 4.2 Launch Antigravity via the proxy

**Option 1: Using the Launch Script (Recommended)**

```bash
cd ~/path/to/antigravity-proxy
./scripts/launch-antigravity.sh

```

This script automatically sets `HTTP_PROXY` and `HTTPS_PROXY` to `http://localhost:8080` and launches the application.

**Option 2: Manual Launch**

```bash
HTTP_PROXY=http://localhost:8080 \
HTTPS_PROXY=http://localhost:8080 \
/Applications/Antigravity.app/Contents/MacOS/Antigravity

```

> **Note**: Antigravity **must** be started with these proxy environment variables for the interception to work.

### 4.3 Verify Gemini Traffic

Trigger any AI feature in Antigravity (e.g., chat, code generation). In the proxy terminal, you should see:

```text
📥 INCOMING REQUEST
   URL: https://generativelanguage.googleapis.com/...
   🔄 Replaced key in header

```

This confirms that Antigravity is using your organization's Gemini Code Assist key.

---

## 5. Integration into Org Documentation

When listing supported IDEs in your internal documentation, you can include Antigravity as a first-class citizen:

> - **VS Code**: Install "Gemini Code Assist" from the Marketplace.
> - **JetBrains**: Install the "Gemini Code Assist" plugin.
> - **Antigravity**:
>   1. Install and configure `antigravity-proxy` locally.
>   2. Set your `GEMINI_API_KEY` in `.env`.
>   3. Start the proxy: `mitmproxy -s mitmproxy-addon.py --listen-port 8080`.
>   4. Launch Antigravity: `./scripts/launch-antigravity.sh`.
>   5. *Result*: Antigravity uses the organization's Gemini Code Assist Standard/Enterprise key.

---

## 6. Notes, Limitations, and Security



1. **Unofficial Integration**: This is a community-driven proxy solution, not an official Google extension.


2. **MITM Security**: The trusted mitmproxy CA can intercept *all* HTTPS traffic from your machine. Use this only on personal development machines, never on shared or production systems. Ensure the proxy listens only on localhost.


3. **API Key Safety**: Never commit `.env` to version control.


4. **Enterprise Features**: This setup swaps credentials. Enterprise features controlled by the API key (quotas, data logging policies) will apply, but IDE-specific UI features of the official plugin may not be present.

---

## 7. Quick Start (Copy-Paste)

For experienced macOS users, here is the condensed setup:

```bash

# 1. Install dependencies

brew install mitmproxy
pip3 install python-dotenv

# 2. Setup Proxy

git clone https://github.com/elad12390/antigravity-proxy.git
cd antigravity-proxy
cp .env.example .env

# EDIT .env: Set GEMINI_API_KEY=your_key

# 3. Trust Cert

mitmproxy # Run once, then quit (q)
open ~/.mitmproxy/mitmproxy-ca-cert.pem

# Action: Set to "Always Trust" in Keychain

# 4. Run (Daily)

# Terminal A:

mitmproxy -s mitmproxy-addon.py --listen-port 8080

# Terminal B:

./scripts/launch-antigravity.sh

```

Sources:
[1] elad12390/antigravity-proxy - GitHub https://github.com/elad12390/antigravity-proxy

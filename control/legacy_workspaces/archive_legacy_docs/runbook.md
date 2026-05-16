# Project Runbook (CTO Edition)

## 0) Stack & Assumptions

* Node **20 LTS** (or 22).
* Hardhat + TypeScript.
* OpenAI API (chat + images).
* Ethereum testnet (prefer **Sepolia**; keep **Goerli** only if your RPC still supports it).
* Optional: GitHub Packages or API (requires **GITHUB_TOKEN**).

---

## 1) Prerequisites

```bash
node -v     # >= 20.x
npm -v
```

Recommended global tooling:

```bash
npm i -g npm@latest
```

---

## 2) Clone & Install

```bash
git clone <REPO_URL>
cd <REPO_DIR>
npm install
```

If you pull **GitHub Packages**, configure `.npmrc` (see §6).

---

## 3) Repo Layout (minimum)

```
.
├─ contracts/                 # keep present even if empty
├─ scripts/
│  └─ deploygpt4.ts          # main deploy / GPT integration script
├─ hardhat.config.ts
├─ .env                       # secrets (never commit)
├─ .gitignore
└─ package.json
```

---

## 4) Environment & Secrets

Create `.env` (or copy from `.env.example` if you have one):

```ini
# OpenAI
OPENAI_API_KEY=sk-...

# Testnet - Goerli (legacy) OR Sepolia (preferred)
GOERLI_PRIVATE_KEY=0xabc...           # test wallet ONLY
GOERLI_URL=https://eth-goerli.g.alchemy.com/v2/<key>

# If using Sepolia instead:
SEPOLIA_PRIVATE_KEY=0xabc...
SEPOLIA_URL=https://eth-sepolia.g.alchemy.com/v2/<key>

# If repo/packages require GitHub access:
GITHUB_TOKEN=github_pat_...
```

**Security:**

* Ensure `.gitignore` contains:

  ```
  .env
  ```
* Never commit private keys or API keys.
* Use a **throwaway test wallet** for testnets.

---

## 5) Hardhat Config (TypeScript)

`hardhat.config.ts` (merge with yours if it already exists):

```ts
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";
dotenv.config();

const GOERLI_URL = process.env.GOERLI_URL || "";
const GOERLI_PK  = process.env.GOERLI_PRIVATE_KEY || "";
const SEPOLIA_URL = process.env.SEPOLIA_URL || "";
const SEPOLIA_PK  = process.env.SEPOLIA_PRIVATE_KEY || "";

const config: HardhatUserConfig = {
  solidity: "0.8.24",
  networks: {
    // Keep if your infra still supports Goerli
    goerli: {
      url: GOERLI_URL,
      accounts: GOERLI_PK ? [GOERLI_PK] : [],
    },
    // Preferred testnet
    sepolia: {
      url: SEPOLIA_URL,
      accounts: SEPOLIA_PK ? [SEPOLIA_PK] : [],
    },
  },
};

export default config;
```

---

## 6) GitHub Token (if needed)

If you install **private packages** or call GitHub API:

1. Create token: GitHub → Settings → Developer settings → **Fine-grained tokens** → Generate.

   * **Repository access:** the needed repo(s).
   * **Permissions:**

     * Packages: **read** (for GitHub Packages)
     * Repository contents: **read** (for private source)

2. Export it locally:

```bash
export GITHUB_TOKEN=github_pat_...
# Windows PowerShell:
# setx GITHUB_TOKEN "github_pat_..."
# $env:GITHUB_TOKEN="github_pat_..."
```

3. If using **GitHub Packages**, add `.npmrc` in repo root:

```ini
@your-scope:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

Replace `@your-scope` (e.g., `@ehanc69`) to match your package scope.

---

## 7) OpenAI Integration Touchpoints

From your notes:

* **API key** is read early in `scripts/deploygpt4.ts` (around line ~11).
* **Chat API calls** around lines ~17 and ~96.
* **Images (DALL·E)** around line ~277.

Typical up-to-date client usage:

```ts
// scripts/_openai.ts (optional helper)
import OpenAI from "openai";

export const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!,
});

// Chat example:
export async function askGPT(msg: string) {
  const res = await openai.chat.completions.create({
    model: "gpt-4o-mini",           // adjust to your contract
    messages: [{ role: "user", content: msg }],
  });
  return res.choices[0]?.message?.content ?? "";
}

// Image example:
export async function genImage(prompt: string) {
  const img = await openai.images.generate({
    model: "gpt-image-1",
    prompt,
  });
  return img.data[0]?.url ?? "";
}
```

In `deploygpt4.ts`, import these helpers for clean separation.

---

## 8) NPM Scripts (DX)

Add to `package.json`:

```json
{
  "scripts": {
    "clean": "rimraf cache artifacts typechain",
    "typecheck": "tsc --noEmit",
    "compile": "hardhat compile",
    "deploy:local": "hardhat run scripts/deploygpt4.ts",
    "deploy:goerli": "hardhat run scripts/deploygpt4.ts --network goerli",
    "deploy:sepolia": "hardhat run scripts/deploygpt4.ts --network sepolia",
    "lint": "eslint .",
    "format": "prettier -w ."
  },
  "devDependencies": {
    "@nomicfoundation/hardhat-toolbox": "^5.0.0",
    "dotenv": "^16.4.0",
    "eslint": "^9.0.0",
    "prettier": "^3.3.0",
    "rimraf": "^6.0.0",
    "ts-node": "^10.9.2",
    "typescript": "^5.6.0"
  }
}
```

---

## 9) Local Run

```bash
# compile first (surfaces Solidity & types issues)
npx hardhat compile

# run your script locally (no chain interaction beyond RPC calls included there)
npx hardhat run scripts/deploygpt4.ts
```

---

## 10) Deploy to Testnet

**Goerli** (legacy):

```bash
npx hardhat run scripts/deploygpt4.ts --network goerli
```

**Sepolia** (preferred):

```bash
npx hardhat run scripts/deploygpt4.ts --network sepolia
```

> Fund the test wallet with test ETH for the target network.
> If you verify contracts, add Etherscan key and `hardhat-etherscan`.

---

## 11) Troubleshooting

* **`Error: missing OPENAI_API_KEY`**
  Ensure `.env` exists and `dotenv.config()` is called before using `process.env`.

* **`npm ERR! 401 Unauthorized` during install**
  If using GitHub Packages, confirm `.npmrc` scope matches package name and `GITHUB_TOKEN` has **read:packages**.

* **`insufficient funds` on deploy**
  Fund the testnet account; confirm you're on the right network.

* **Goerli RPC deprecation**
  Switch to Sepolia (add `SEPOLIA_URL`/`SEPOLIA_PRIVATE_KEY` and run `--network sepolia`).

---

## 12) Security Checklist (fast pass)

* `.env` ignored by git.
* Use **test** wallets only on testnets.
* Rotate **GITHUB_TOKEN** and **OPENAI_API_KEY** periodically.
* Consider pre-commit secret scanning (e.g., `gitleaks`) and CI dotenv presence checks.

---

## 13) Optional: Contract Verification (Etherscan)

Install:

```bash
npm i -D @nomicfoundation/hardhat-verify
```

Extend config:

```ts
import "@nomicfoundation/hardhat-verify";
// ...
// etherscan: { apiKey: { sepolia: process.env.ETHERSCAN_API_KEY || "" } }
```

Verify:

```bash
npx hardhat verify --network sepolia <DEPLOYED_ADDRESS> "constructor" "args"
```

---

### One-liners to bootstrap from scratch

```bash
# Create skeleton if needed
npm i -D hardhat @nomicfoundation/hardhat-toolbox typescript ts-node dotenv
npx hardhat      # choose "Create a TypeScript project"
mkdir -p scripts contracts
```

---

If you want this tailored line-by-line to your actual `deploygpt4.ts` and README, paste those files (or connect the repo) and I'll fold the exact references in.

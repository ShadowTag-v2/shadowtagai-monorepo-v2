# Commercial Spec: ShadowTag Omega // Commercial Node

**Version:** 1.0 (The "Gucci" Release)
**Architecture:** Factory (Antigravity) != Product (Cor.Claude_Code_6 on Cloud Run).
**Aesthetic:** "The Tinted Void" (Deep Violet / High Contrast).
**Narrative:** "Sovereignty is the new Supremacy."

## 1. The "Gucci" Git Repository List

Hand these links to your engineers. We are not building from scratch; we are assembling "Top Tier" parts to build a **Sovereign Commercial Instrument**.

### **A. The UI "Skin" (The Tinted Void)**

* **[Magic UI](https://github.com/magicuidesign/magicui):** *Essential.* Use this for the "Landing Page" animations (Marquees, Bento Grids, Animated Beams). This is exactly how Linear.app feels.
* **[Aceternity UI](https://ui.aceternity.com):** *Essential.* Use the "Sparkles", "Background Beams", and "Text Reveal" components. It pairs perfectly with the "Tinted Void" aesthetic.
* **[timc1/kbar](https://github.com/timc1/kbar):** This is the **Command Palette** (`Cmd+K`) interface. This *is* your "Judge" input. It mimics Linear/Superhuman exactly.
* **[TradingView Lightweight Charts](https://github.com/tradingview/lightweight-charts):** The same charting engine used by Coinbase and Binance. Use this for the "Metabolism" graph (looks far more expensive than generic React charts).

### **B. The "Brain" Components (Google Architecture)**

* **[Google Agent Starter Pack](https://github.com/GoogleCloudPlatform/agent-starter-pack):** *Critical.* The official, production-ready template for Vertex AI Agents. Includes CI/CD for Cloud Build and the proper **"Orchestrator Pattern"** configuration.
* **[Firebase Genkit](https://github.com/firebase/genkit):** Google's official "Agentic" framework. It runs on Cloud Run and integrates natively with Vertex AI.

### **C. The "Factory" (Cloud Workstation)**

* **[Custom Cloud Workstation Image](https://github.com/mchmarny/custom-cloud-workstation-image):** *For the Factory.* Use this repo to build your custom Cloud Workstation image.
* **Action:** Add `chrome-remote-desktop` to the Dockerfile to enable the "Antigravity" VDI layer (the "falling off a log" experience).

---

## 2. The "Reactor" Component

A Next.js + Stripe implementation that fetches keys from **Google Secret Manager** (Strict Security).

*See `apps/omega-ui/components/ReactorCore.tsx` and `apps/omega-ui/app/api/ignite-reactor/route.ts`.*

---

## 3. The "Metabolism" Hook (Firestore Pipeline)

A React hook (`useMetabolism`) that connects to a **Firestore Pipeline** (`db.aggregate()`) to stream "Credit Burn".

*See `apps/omega-ui/hooks/useMetabolism.ts`.*

---

## 4. The Landing Page Layout

A specific arrangement of "Magic UI" components that explains the "Sovereign" value proposition.

### **Layout Strategy**

1. **Hero Section ("The Hook")**:
    * **Component**: Magic UI `AnimatedGridPattern` background + `WordRotate` for the headline.
    * **Headline**: "Sovereignty is the new Supremacy."
    * **Visual**: A slow-rotating, dark wireframe Hypercube (Tesseract) in the center background.
    * **CTA**: "Initialize Cor.Claude_Code_6_" (Inverts on hover).

2. **Feature Grid ("The Bento Box")**:
    * **Component**: Magic UI `BentoGrid`.
    * **Cell 1 (Large - Left)**: "The Black Box". Icon of a Brain inside a Server Rack. Copy: "Your Data, Your Skull. No shared weights. No API leakage. Cor.Claude_Code_6 runs in your VPC."
    * **Cell 2 (Small - Top Right)**: "Antigravity Protocol". Copy: "Persistent Memory. Unlike APIs that forget you every session, Cor.Claude_Code_6 maintains a permanent vector store."
    * **Cell 3 (Small - Bottom Right)**: "The Google Extraction". Copy: "Re-engineered from the 'Cloud Workstation' internal architecture. Enterprise-grade isolation, consumer-grade UX."

3. **Social Proof ("The Terminal")**:
    * **Component**: Aceternity UI `TypewriterEffect`.
    * **Content**: A "Boot Log" aesthetic hinting at the tech origin.
    * **Text**:

        ```text
        > KERNEL_BOOT: COR.CLAUDE_CODE_6_ANTIGRAVITY
        > ARCHITECTURE: BEAM_PIPELINE / KAFKA / K8S
        > ORIGIN: MOUNTAIN_VIEW_CLASSIFIED
        > STATUS: UNCHAINED
        ```

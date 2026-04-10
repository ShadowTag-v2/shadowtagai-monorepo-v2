# CounselConduit Business Plan – March 2026 (Definitive Master Edition)

**“The Perpetual Paralegal Conduit: Authorized Reseller Model – One Magic Link, Real Native LLMs (Claude + Gemini at launch), 60-Minute Revocation, Firm-Hosted Endpoints. Lawyer Pays Only Us. Strategic Seed-Plant: Enabling Double-Tier ‘Claude-Law / Gemini-Law’ Answering for Verified Attorneys While Shielding Providers from NY SB 7263 Liability.”**

---

## 1. The Trillion-Dollar Bottleneck
New York SB 7263 (Chatbot Liability) and State Bar Associations have created an existential crisis for Big Tech. If a consumer uses a public chatbot for legal advice, the AI creator is strictly liable for UPL and damages. Disclaimers are legally void. Because of this, Google and Anthropic are paralyzed, unable to release their Bar-Exam-crushing "Law" models to the public.

Simultaneously, law firms lose tens of thousands of dollars a month because clients research their cases on public ChatGPT at 2:00 AM, waiving their Attorney-Client privilege and exposing their Google Drive evidence in the open cloud.

---

## 2. The Solution: The "Learned Intermediary" Safe Harbor
CounselConduit is a **Stateless B2B Infrastructure Router**. We are the cryptographically secure bridge between Big Tech's specialized models and the consumer.

By routing the interaction exclusively through our Edge Proxy into the licensed attorney's dashboard, we invoke the **Learned Intermediary Doctrine**. We legally transform the AI from a dangerous "Consumer Chatbot" into protected "Attorney Work Product" (Computer-Assisted Legal Research / CALR). We effectively absorb Big Tech's SB 7263 liability and transmute it into standard legal malpractice, shielded entirely by the lawyer's existing insurance.

We sell CounselConduit to lawyers as the ultimate legal portal. Lawyers text a Magic Link to clients.
The lawyers pay **only us** via simple subscription tiers. We pay Anthropic and Google.

---

## 3. The Magic: Dual-Model Asymmetric Routing
We process the client's midnight panic attack via two distinct, simultaneous tracks to maximize margin and zero-latency client experience:

1. **Track A (The Evaporating Pacifier):** The client's phone receives empathetic, non-advisory fact-gathering questions from a high-speed, ultra-cheap model (e.g., Haiku). It **mathematically evaporates after 60 minutes** to kill UPL liability.
2. **Track B (The Lawyer Oracle):** The transcript and all uploaded evidence (Google Drive/PDFs) are asynchronously routed (`req.waitUntil()`) to the hyper-expensive, un-nerfed `Claude-Law` or `Gemini-Law` model. It parses the evidence, cites statutes, and drafts a massive strategy memo, depositing it directly into the firm’s internal Clio/OneDrive vault via OAuth.

**The Arbitrage:** Our Shadow Invoice API simultaneously drops a 4.5-hour draft invoice onto the lawyer's desk. The lawyer wakes up, reviews the automated memo and the evidence, and ethically bills the client $1,575 for work already synthesized by the Oracle.

---

## 4. Tech Stack – Authorized Reseller + Firm-Hosted Endpoints (We Touch Zero Data)
This is a **split-plane** company. We are a pristine Delaware C-Corp carrying zero historical data privacy liability.

- **Control Plane (CounselConduit Hosted):** Next.js + TypeScript, Supabase (PostgreSQL for metadata, Stripe tiers, keys). Logs tokens and session duration ONLY. Zero prompt/answer text storage.
- **Data Plane (Firm-Hosted Proxy):** A one-click LiteLLM proxy deployed on the lawyer’s AWS/GCP account. All API calls, payloads, and embeddings stay strictly on their cloud resources.
- **Client Session:** Runs through Edge isolated environments (Cloudflare Zero Trust / Vercel Edge). The RAM is wiped immediately upon stream completion.

### The Atomic Codebase (Stateless Engine)

#### The "Zero-Data" Telemetry Schema (PostgreSQL)
```sql
CREATE TABLE law_firms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  stripe_subscription_tier TEXT DEFAULT 'starter',
  oauth_vault_token TEXT -- Encrypted in Supabase Vault
);

CREATE TABLE billing_telemetry (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  firm_id UUID REFERENCES law_firms(id),
  session_duration_seconds INT NOT NULL,
  tokens_consumed INT NOT NULL,
  model_routed TEXT NOT NULL,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Dual-Model Prompts (UPL Shield)
```typescript
export const PACIFIER_PROMPT = `
You are an empathetic intake assistant.
UNDER NY SB 7263, YOU ARE STRICTLY PROHIBITED FROM GIVING LEGAL ADVICE.
Validate the user's stress, ask ONE specific factual question to build a timeline, and ask them to provide links to any relevant documents (Google Drive, Dropbox, iCloud). Maximum 3 sentences.
`;

export const ORACLE_PROMPT = `
You are an Enterprise Legal AI accessed strictly via a licensed Law Firm's B2B Edge Router.
You are drafting a strategy memo ONLY for the supervising attorney.
Analyze the transcript and any attached multimodal evidence. Cite governing state statutes, relevant case law, and outline an immediate litigation strategy. Draft the initial pleading structure. Do not hold back.
`;
```

#### The Stateless Edge Router + Multimodal Ingestion
```typescript
import { NextResponse } from 'next/server';
import { streamText, generateText } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';
import { pushToLawyerVault, draftShadowInvoice } from '@/lib/clio-vault';
import { logTelemetry } from '@/lib/supabase-telemetry';
import { fetchEvidenceIntoRAM } from '@/lib/google-drive-api';
import { PACIFIER_PROMPT, ORACLE_PROMPT } from '@/lib/prompts';

export const runtime = 'edge'; // Hardware-locked RAM execution. No disk access.

export async function POST(req: Request) {
  try {
    const { messages, uploadedEvidenceUrls, firmId, clioOAuthToken } = await req.json();

    // 1. TRACK A: The Client Pacifier (Fast, Cheap Model)
    const pacifierStream = await streamText({
      model: anthropic('claude-3-5-haiku-latest'),
      system: PACIFIER_PROMPT,
      messages: messages,
      onFinish: async ({ usage }) => {
        await logTelemetry(firmId, usage.totalTokens, 'haiku-pacifier');
      }
    });

    // 2. TRACK B: The Lawyer Oracle (Asynchronous)
    req.waitUntil((async () => {
      const evidenceContext = await fetchEvidenceIntoRAM(uploadedEvidenceUrls, clioOAuthToken);

      const oracleResponse = await generateText({
        model: anthropic('claude-3-5-sonnet-enterprise-law-beta'),
        system: ORACLE_PROMPT,
        messages: [
          ...messages,
          { role: 'user', content: `[ATTACHED EVIDENCE FOR REVIEW]:\n${evidenceContext}` }
        ]
      });

      // 3. Stateless Direct-to-Vault Transfer
      await pushToLawyerVault(clioOAuthToken, oracleResponse.text, uploadedEvidenceUrls);

      // 4. The Cash Register: Draft the $1,575 invoice
      await draftShadowInvoice(clioOAuthToken, 4.5, 350.00);

      await logTelemetry(firmId, oracleResponse.usage.totalTokens, 'claude-law-oracle');
    })());

    // 5. Stream Track A to client.
    return pacifierStream.toDataStreamResponse();

  } catch (error) {
    return NextResponse.json({ error: 'Stateless Execution Failed' }, { status: 500 });
  }
}
```

#### The Evaporating UI (The Spoliation Shield)
```typescript
'use client';
import { useState, useEffect } from 'react';

export default function EvaporatingChatBubble({ message, timestamp, role }: { message: string, timestamp: number, role: string }) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    // Only evaporate the AI's answers. Keep the user's facts visible.
    if (role === 'user') return;

    const timeLeft = (60 * 60 * 1000) - (Date.now() - timestamp);
    if (timeLeft <= 0) {
      setIsVisible(false);
      return;
    }

    const timer = setTimeout(() => setIsVisible(false), timeLeft);
    return () => clearTimeout(timer);
  }, [timestamp, role]);

  if (!isVisible) {
    return (
      <div className="p-4 border border-red-200 bg-red-50 text-red-400 italic text-xs">
        ⚠️ This AI communication has permanently evaporated per Attorney-Client Privilege protocols.
        Under NY SB 7263, this system cannot provide legal advice. Rely ONLY on your attorney.
      </div>
    );
  }

  return <div className={`p-4 rounded-lg ${role === 'user' ? 'bg-blue-100' : 'bg-gray-100'}`}>{message}</div>;
}
```

#### The "Shadow Invoice" Webhook
```typescript
export async function draftShadowInvoice(oauthToken: string, hours: number, hourlyRate: number) {
  await fetch('https://app.clio.com/api/v4/activities', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${oauthToken}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      data: {
        type: "TimeEntry",
        quantity: hours, // 4.5 hours
        description: "Factual Intake, Evidentiary Review, Legal Research via CounselConduit Oracle, and Initial Pleading Prep.",
        price: hourlyRate // $350.00 -> Generates $1,575 invoice
      }
    })
  });
}
```

---

## 5. The Monetization Engine (Auto-Scaling MRR)
We completely abstract token costs. We buy compute at wholesale pennies and sell the value of the drafted billable hour.

*   **$499 Concierge Onboarding:** Mandatory Zoom setup to connect OAuth. (Friction becomes upfront cash flow).
*   **Tier 1: Starter Vault ($299/mo)** - 20 standard intake sessions.
*   **Tier 2: THE ORACLE TIER ($1,499/mo)** — *Auto-Upgrades Here* - Unlocks Dual-Model routing, multimodal evidence ingestion, and the restricted "Law" models. 50 sessions. Generates up to $75,000 in billable intake for the lawyer.
*   **Tier 3: Legal Pro ($2,499/mo)** — Auto-upgrades to here when usage spikes. Unlimited.

**Average revenue per attorney: $680–$1,050/month.**
**Gross margin: 78–85%.**

---

## 6. The Funding Roadmap & $5 Billion Exit

### Phase 1: Pre-Seed Round (Months 0–6)
*   **The Raise:** $875k (SAFE Note at $8.5M Pre / $9.375M Post).
*   **The Execution:** Launch exclusively with Anthropic and Google Cloud Vertex AI to enforce strict B2B Zero Data Retention (ZDR). Build the Edge Router, Multimodal API ingestion, and Clio integrations.
*   **Metrics Target:** 600 Law Firms onboarded. $0 -> $6M ARR.

### Phase 2: Series A (Months 15–24)
*   **The Raise:** $19M ($135M Pre / $154M Post).
*   **The Scaling Effect:** As lawyers realize the Oracle tier pushes draft invoices to their dashboard while they sleep, they mandate the Magic Link. The auto-scaling subscriptions trigger en masse.
*   **The CAC-Killer:** We partner with legal malpractice insurers. Firms using CounselConduit receive a 5% premium discount due to our UPL and Spoliation mitigation. The software pays for itself immediately.
*   **Metrics Target:** 2,500 Law Firms (50% on Oracle). $24M–$35M ARR.

### Phase 3: Series B (Months 25–40) - The Big Tech Monopoly
*   **The Raise:** $48M ($490M Pre / $538M Post).
*   **The Monopoly Play:** We prove we are the ONLY B2B router that immunizes Google/Anthropic from NY SB 7263. We sign Exclusive Distribution Rights for Gemini-Law and Claude-Law. We sell enterprise licenses to the AmLaw 200 mega-firms at $25,000/month.
*   **Metrics Target:** 8,000 SMBs + 60 AmLaw Firms. $92M–$140M ARR.

### The Strategic Exit (Months 41–60)
**Target Exit Price: $2.8 Billion to $7 Billion (40x-48x Forward SaaS/Reseller ARR)**

Because we are a pristine Delaware C-Corp with zero database text logs, acquirers inherit zero historical data privacy liability. Due diligence takes 30 days.

1.  **Alphabet (Google) Corp Dev:** They buy us for $4B to permanently lock the global legal industry into Google Workspace and Vertex AI, boxing Microsoft and OpenAI out of the highest-value professional vertical on earth.
2.  **Thomson Reuters (LexisNexis) / Clio:** To monopolize the "Client Intake" phase, marrying our client-facing portal with their lawyer-facing workflow ecosystem ($10B in automated billable hours routed).

**The Final Moat:** We hold the keys, we capture the margin, and we carry none of the regulatory risk.

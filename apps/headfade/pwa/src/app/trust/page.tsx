import React from 'react';

export default function TrustCenter() {
  return (
    <div className="min-h-screen bg-black text-white p-8 font-sans selection:bg-purple-900 selection:text-white">
      <div className="max-w-4xl mx-auto mt-20">
        <header className="mb-16 border-b border-white/10 pb-12">
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
            ShadowTag AI Trust Manifesto
          </h1>
          <p className="text-xl text-zinc-400 max-w-2xl">
            We weaponize compliance as a competitive moat. Our platform is engineered from the
            ground up for zero-trust security, ensuring your enterprise assets remain completely
            sovereign.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
          <div className="p-8 bg-zinc-900/50 border border-zinc-800 rounded-xl hover:border-purple-500/50 transition-colors">
            <h2 className="text-2xl font-semibold mb-4 text-purple-400">
              1. ZDR (Zero Data Retention) — The Prime Directive
            </h2>
            <div className="text-zinc-400 space-y-4 text-sm leading-relaxed">
              <p>
                <strong className="text-zinc-300">The Enterprise Fear:</strong> Companies are
                terrified of employees pasting proprietary code, financial data, or patient records
                into an AI prompt, only for it to be stored in a shadow database and regurgitated by
                a public model.
              </p>
              <p>
                <strong className="text-zinc-300">Our Stance: &quot;Stateless AI.&quot;</strong> We
                do not log, store, cache, or look at your AI payloads. ShadowTag operates on a
                strict Zero Data Retention (ZDR) architecture. Prompts and context windows are
                processed entirely in volatile memory (RAM) and are instantly vaporized the
                millisecond the inference is returned to the client.
              </p>
              <p>
                <strong className="text-zinc-300">The Guarantee:</strong> We train on absolutely
                nothing. If our databases are breached, hackers find an empty room.
              </p>
            </div>
          </div>

          <div className="p-8 bg-zinc-900/50 border border-zinc-800 rounded-xl hover:border-purple-500/50 transition-colors">
            <h2 className="text-2xl font-semibold mb-4 text-purple-400">
              2. The U.S. CLOUD Act — Cryptographic Immunity
            </h2>
            <div className="text-zinc-400 space-y-4 text-sm leading-relaxed">
              <p>
                <strong className="text-zinc-300">The Enterprise Fear:</strong> European clients
                hesitate to buy from U.S. startups because the U.S. CLOUD Act allows federal
                agencies to subpoena data from U.S. tech companies, even if those servers are
                physically located in Europe.
              </p>
              <p>
                <strong className="text-zinc-300">
                  Our Stance: &quot;You cannot subpoena what does not exist.&quot;
                </strong>{' '}
                Most companies fight government overreach with armies of lawyers; we fight it with
                architecture. We neutralize the CLOUD Act through our ZDR pipeline and BYOK (Bring
                Your Own Key) encryption for user accounts. Even under a federal gag order or
                warrant, we cannot surrender your proprietary IP because we do not have it. For any
                persistent workspace data, the enterprise holds the master decryption key—meaning we
                can only hand the government mathematically unbreakable ciphertext.
              </p>
            </div>
          </div>

          <div className="p-8 bg-zinc-900/50 border border-zinc-800 rounded-xl hover:border-purple-500/50 transition-colors">
            <h2 className="text-2xl font-semibold mb-4 text-purple-400">
              3. Data Residency — The Geographic Moat
            </h2>
            <div className="text-zinc-400 space-y-4 text-sm leading-relaxed">
              <p>
                <strong className="text-zinc-300">The Enterprise Fear:</strong> Highly regulated
                industries (finance, defense, healthcare) legally mandate that their data must never
                cross international fiber-optic borders.
              </p>
              <p>
                <strong className="text-zinc-300">
                  Our Stance: &quot;Your data. Your sovereign soil.&quot;
                </strong>{' '}
                We treat data residency as a strict routing constraint. For enterprise deployments,
                we utilize geographic ring-fencing. If an EU client connects to ShadowTag, their API
                calls are routed exclusively to isolated, single-tenant clusters in the EU (e.g.,
                AWS Frankfurt or GCP Paris). Your data never crosses the Atlantic.
              </p>
            </div>
          </div>

          <div className="p-8 bg-zinc-900/50 border border-zinc-800 rounded-xl hover:border-purple-500/50 transition-colors">
            <h2 className="text-2xl font-semibold mb-4 text-purple-400">
              4. GDPR — Privacy by Architecture
            </h2>
            <div className="text-zinc-400 space-y-4 text-sm leading-relaxed">
              <p>
                <strong className="text-zinc-300">The Enterprise Fear:</strong> Massive fines for
                using vendor software that mismanages the Personally Identifiable Information (PII)
                of European citizens.
              </p>
              <p>
                <strong className="text-zinc-300">
                  Our Stance: &quot;Compliance via Non-Applicability.&quot;
                </strong>{' '}
                We don&apos;t just sign standard Data Processing Agreements (DPAs); we design GDPR
                into the codebase. Because we run a ZDR pipeline, we inherently minimize the PII
                footprint—drastically reducing the liability of being a &quot;Data Controller.&quot;
                Furthermore, we do not require manual IT support tickets for data deletion; we
                expose a 1-click &quot;Nuke My Data&quot; API that instantly triggers the Right to
                be Forgotten, cryptographically shredding all associated user auth and billing data
                across our infrastructure.
              </p>
            </div>
          </div>
        </div>

        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-6">Firewall &amp; Network Configuration</h2>
          <div className="p-6 bg-black border border-zinc-800 rounded-xl font-mono text-sm text-zinc-300">
            <p className="mb-2"># For Enterprise IT / Network Administrators</p>
            <p className="mb-2">
              # To prevent Palo Alto / Corporate Firewall blocks, please allowlist:
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-4 text-zinc-400">
              <li>headfade.com</li>
              <li>*.headfade.com</li>
              <li>shadowtagai.com</li>
              <li>*.shadowtagai.com</li>
              <li>headfade-mcp-*.run.app</li>
            </ul>
          </div>
        </section>

        <footer className="text-center text-sm text-zinc-500 mt-20 pb-8">
          <p>&copy; 2026 ShadowTagAI Inc. All rights reserved. Sovereign AI for the Enterprise.</p>
        </footer>
      </div>
    </div>
  );
}

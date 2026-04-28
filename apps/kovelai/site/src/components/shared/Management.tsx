// Copyright (c) 2026 ShadowTag, Inc. All rights reserved. Dual-Licensed under CounselConduit Compliance.

export default function Management() {
  return (
    <section className="py-20 md:py-28 bg-surface-lowest" id="management">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">Leadership</div>
        <h2 className="section-title">Management</h2>
        <div className="ceo-card mt-10">
          <div className="ceo-headshot bg-surface-high flex items-center justify-center text-gold text-3xl font-bold">
            EH
          </div>
          <div>
            <h3 className="text-lg font-semibold text-primary-text mb-1">Erik Hancock</h3>
            <div className="text-sm text-gold mb-3">Founder &amp; CEO</div>
            <p className="text-sm leading-relaxed text-secondary-text">
              Erik founded KovelAI after watching the post-<em>Heppner</em> landscape expose a
              dangerous gap: clients were flooding attorneys with discoverable AI searches,
              incorrect legal opinions from ChatGPT, and Google rabbit holes — all of it available
              to opposing counsel. His mission: give every attorney a turnkey portal to deploy for
              their clients. The client searches freely and relaxes enough to recall all the facts
              of their case. The attorney sits in the loop — monitoring sessions, providing the
              first legal opinion, and billing automatically. We protect the client from themselves.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

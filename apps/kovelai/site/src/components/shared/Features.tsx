// Copyright (c) 2026 ShadowTag, Inc. All rights reserved. Dual-Licensed under CounselConduit Compliance.

export default function Features() {
  const features = [
    {
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 256 256"
          fill="none"
          stroke="currentColor"
          strokeWidth="16"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-gold"
          aria-hidden="true"
          role="presentation"
        >
          <path
            d="M128 24a104 104 0 1 0 104 104A104.11 104.11 0 0 0 128 24Z"
            opacity=".2"
            fill="currentColor"
          />
          <circle cx="128" cy="128" r="104" fill="none" />
          <path d="M128 80v96M176 128H80" />
        </svg>
      ),
      title: "Your Firm's Client Portal",
      desc: 'You deploy a branded, secure research environment for your clients. They search the web, use AI, and explore their case through a privilege-protected connection to your firm. Their research stays shielded from discovery because it never leaves your umbrella. No IT department required — deploy in minutes.',
    },
    {
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 256 256"
          fill="none"
          stroke="currentColor"
          strokeWidth="16"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-gold"
          aria-hidden="true"
          role="presentation"
        >
          <rect x="48" y="48" width="160" height="160" rx="8" opacity=".2" fill="currentColor" />
          <rect x="48" y="48" width="160" height="160" rx="8" fill="none" />
          <path d="M48 128h160M128 48v160" />
        </svg>
      ),
      title: 'Attorney Oversight Dashboard',
      desc: 'You sit in the loop on every client session. See what your clients are searching, what AI responses they receive, and when they are active. No more getting ambushed by a client sending you random, incorrect AI-generated legal opinions. You give the first legal opinion — not ChatGPT.',
    },
    {
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 256 256"
          fill="none"
          stroke="currentColor"
          strokeWidth="16"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-gold"
          aria-hidden="true"
          role="presentation"
        >
          <path
            d="M40 114.79V208a8 8 0 0 0 8 8H208a8 8 0 0 0 8-8V114.79a8 8 0 0 0-3.56-6.66l-80-53.34a8 8 0 0 0-8.88 0l-80 53.34A8 8 0 0 0 40 114.79Z"
            opacity=".2"
            fill="currentColor"
          />
          <path
            d="M40 114.79V208a8 8 0 0 0 8 8H208a8 8 0 0 0 8-8V114.79a8 8 0 0 0-3.56-6.66l-80-53.34a8 8 0 0 0-8.88 0l-80 53.34A8 8 0 0 0 40 114.79Z"
            fill="none"
          />
        </svg>
      ),
      title: 'Automatic Credit Card Billing',
      desc: "Your client's credit card is both their login credential and their payment method. You set the rate in compliance with the Rules of Professional Responsibility. They're billed at the end of each cycle — automatically. No invoicing, no collections, no overhead. You get paid while they get protected.",
    },
    {
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 256 256"
          fill="none"
          stroke="currentColor"
          strokeWidth="16"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-gold"
          aria-hidden="true"
          role="presentation"
        >
          <path
            d="M213.67 186.15A8 8 0 0 1 208 200H48a8 8 0 0 1-5.67-13.85l80-80a8 8 0 0 1 11.34 0Z"
            opacity=".2"
            fill="currentColor"
          />
          <path
            d="M213.67 186.15A8 8 0 0 1 208 200H48a8 8 0 0 1-5.67-13.85l80-80a8 8 0 0 1 11.34 0Z"
            fill="none"
          />
          <path d="M128 56v64" />
        </svg>
      ),
      title: 'Protect Clients From Themselves',
      desc: 'Your clients will search — with or without you. The question is whether those searches are discoverable. KovelAI puts you in an oversight position on all case-related AI, web search, translation, and transcription. Your client searches at will, relaxes enough to recall all the facts, and the privilege holds.',
    },
    {
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 256 256"
          fill="none"
          stroke="currentColor"
          strokeWidth="16"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-gold"
          aria-hidden="true"
          role="presentation"
        >
          <rect x="32" y="56" width="192" height="144" rx="8" opacity=".2" fill="currentColor" />
          <rect x="32" y="56" width="192" height="144" rx="8" fill="none" />
          <path d="M128 56V32M96 56V40M160 56V40" />
        </svg>
      ),
      title: 'The Heppner Ultimatum',
      desc: 'The conversation with your client is straightforward: "Knowing the Heppner decision, the other side can and will obtain all searching done outside our firm\'s KovelAI portal. Either you do it through us, or proceed at your peril." That single sentence closes the deal — because the stakes are their entire case.',
    },
    {
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 256 256"
          fill="none"
          stroke="currentColor"
          strokeWidth="16"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-gold"
          aria-hidden="true"
          role="presentation"
        >
          <path d="M232 208H24V48" fill="none" />
          <path d="M232 168l-68-68-48 48L72 104" fill="none" />
        </svg>
      ),
      title: 'Another Tool in Your Arsenal',
      desc: 'CounselConduit on KovelAI harnesses AI and web searches into another tool for the attorney to best represent their client. You form legal strategy from privileged intelligence — not damage control from discoverable searches your client did on their own.',
    },
  ];

  return (
    <section className="py-20 md:py-28 bg-surface-lowest" id="features">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">Shield From Discovery — Your Firm&apos;s Infrastructure</div>
        <h2 className="section-title">
          Mandatory Infrastructure. Full Oversight. Automatic Billing.
        </h2>
        <p className="section-desc mb-12">
          You purchase KovelAI as privileged infrastructure for your clients. They search the web,
          use AI, and explore their case through a secure connection to your firm. You monitor every
          session, give the first legal opinion, and bill their credit card automatically. The
          privilege holds. Opposing counsel gets nothing.
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div
              key={f.title}
              className="glass-card group transition-transform duration-200 active:scale-[0.98]"
            >
              <div className="text-2xl mb-3">{f.icon}</div>
              <h3 className="text-base font-semibold text-primary-text mb-2">{f.title}</h3>
              <p className="text-sm leading-relaxed text-secondary-text">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

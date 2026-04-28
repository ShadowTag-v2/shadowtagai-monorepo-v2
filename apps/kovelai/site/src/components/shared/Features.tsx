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
      title: 'Secure Client Research Portal',
      desc: 'Your clients get a branded portal where they can search the web, use AI, and explore their case — all routed through a secure, privilege-protected connection to your firm. Their research stays shielded from discovery.',
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
      title: 'Attorney Monitoring Dashboard',
      desc: 'You sit in the loop on every client session. See what your clients are searching, when they are active, and what AI responses they receive. You give the first legal opinion — not opposing counsel.',
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
      title: 'Automated Credit Card Billing',
      desc: "Your client's credit card is charged at the end of each billing cycle — you set the rate, the payment flows automatically. No invoicing, no collections, no overhead. Fully compliant with the Rules of Professional Responsibility.",
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
      title: 'Client Peace of Mind',
      desc: 'Your clients search whenever anxiety strikes — nights, weekends, 3 AM before a hearing. They finally relax enough to recall all the facts of their case. No discoverable evidence for the other side. No panic. Just clarity.',
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
      title: 'Compliance First',
      desc: 'Pursuing SOC 2 Type II certification. HIPAA-supportive architecture. Built to withstand judicial scrutiny on privilege claims.',
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
      title: 'No More Ambushes',
      desc: 'Instead of your client sending you discoverable AI searches at random times, everything flows through your privileged portal. You see it first. You give the first legal opinion. You form strategy — not damage control.',
    },
  ];

  return (
    <section className="py-20 md:py-28 bg-surface-lowest" id="features">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">What Your Clients Get</div>
        <h2 className="section-title">Everything Your Clients Need to Research Safely</h2>
        <p className="section-desc mb-12">
          CounselConduit protects your clients — not from you, but from the other side. You deploy a
          privileged research portal connected to your firm. Your clients search freely and relax
          before trial. You monitor every session, give the first legal opinion, and bill
          automatically through their credit card.
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

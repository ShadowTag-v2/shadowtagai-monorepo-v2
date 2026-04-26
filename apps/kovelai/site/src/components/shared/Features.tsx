export default function Features() {
  const features = [
    {
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 256 256" fill="none" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round" className="text-gold">
          <path d="M128 24a104 104 0 1 0 104 104A104.11 104.11 0 0 0 128 24Z" opacity=".2" fill="currentColor"/>
          <circle cx="128" cy="128" r="104" fill="none"/>
          <path d="M128 80v96M176 128H80"/>
        </svg>
      ),
      title: 'AI-Powered Intake',
      desc: 'Intelligent after-hours client intake that captures, qualifies, and organizes potential matters while your team rests.',
    },
    {
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 256 256" fill="none" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round" className="text-gold">
          <rect x="48" y="48" width="160" height="160" rx="8" opacity=".2" fill="currentColor"/>
          <rect x="48" y="48" width="160" height="160" rx="8" fill="none"/>
          <path d="M48 128h160M128 48v160"/>
        </svg>
      ),
      title: 'Matter Pipeline',
      desc: 'Every client interaction becomes a tracked, scored, and prioritized entry in your matter pipeline. No leads lost.',
    },
    {
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 256 256" fill="none" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round" className="text-gold">
          <path d="M40 114.79V208a8 8 0 0 0 8 8H208a8 8 0 0 0 8-8V114.79a8 8 0 0 0-3.56-6.66l-80-53.34a8 8 0 0 0-8.88 0l-80 53.34A8 8 0 0 0 40 114.79Z" opacity=".2" fill="currentColor"/>
          <path d="M40 114.79V208a8 8 0 0 0 8 8H208a8 8 0 0 0 8-8V114.79a8 8 0 0 0-3.56-6.66l-80-53.34a8 8 0 0 0-8.88 0l-80 53.34A8 8 0 0 0 40 114.79Z" fill="none"/>
        </svg>
      ),
      title: 'Privileged Search',
      desc: "Clients search the web through your firm\u0027s infrastructure. Every query is privileged, every session is billed.",
    },
    {
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 256 256" fill="none" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round" className="text-gold">
          <path d="M213.67 186.15A8 8 0 0 1 208 200H48a8 8 0 0 1-5.67-13.85l80-80a8 8 0 0 1 11.34 0Z" opacity=".2" fill="currentColor"/>
          <path d="M213.67 186.15A8 8 0 0 1 208 200H48a8 8 0 0 1-5.67-13.85l80-80a8 8 0 0 1 11.34 0Z" fill="none"/>
          <path d="M128 56v64"/>
        </svg>
      ),
      title: 'After-Hours Capture',
      desc: 'Panic calls at 2 AM become organized, retained matters by 8 AM. Your paralegal costs drop, your intake revenue rises.',
    },
    {
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 256 256" fill="none" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round" className="text-gold">
          <rect x="32" y="56" width="192" height="144" rx="8" opacity=".2" fill="currentColor"/>
          <rect x="32" y="56" width="192" height="144" rx="8" fill="none"/>
          <path d="M128 56V32M96 56V40M160 56V40"/>
        </svg>
      ),
      title: 'Compliance First',
      desc: 'Pursuing SOC 2 Type II certification. HIPAA-supportive architecture. Built to withstand judicial scrutiny on privilege claims.',
    },
    {
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 256 256" fill="none" stroke="currentColor" strokeWidth="16" strokeLinecap="round" strokeLinejoin="round" className="text-gold">
          <path d="M232 208H24V48" fill="none"/>
          <path d="M232 168l-68-68-48 48L72 104" fill="none"/>
        </svg>
      ),
      title: 'Revenue Analytics',
      desc: 'Real-time dashboards showing intake conversion, after-hours capture rate, and revenue per privileged session.',
    },
  ];

  return (
    <section className="py-20 md:py-28 bg-surface-lowest" id="features">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">Platform</div>
        <h2 className="section-title">Built for Law Firms That Think Like Businesses</h2>
        <p className="section-desc mb-12">
          KovelAI combines privileged communication infrastructure with AI-powered intake — turning
          your firm&apos;s front door into a revenue engine that never sleeps.
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div key={f.title} className="glass-card group transition-transform duration-200 active:scale-[0.98]">
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

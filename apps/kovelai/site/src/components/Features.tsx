export default function Features() {
  const features = [
    {
      icon: '🤖',
      title: 'AI-Powered Intake',
      desc: 'Intelligent after-hours client intake that captures, qualifies, and organizes potential matters while your team rests.',
    },
    {
      icon: '📊',
      title: 'Matter Pipeline',
      desc: 'Every client interaction becomes a tracked, scored, and prioritized entry in your matter pipeline. No leads lost.',
    },
    {
      icon: '🛡️',
      title: 'Privileged Search',
      desc: "Clients search the web through your firm's infrastructure. Every query is privileged, every session is billed.",
    },
    {
      icon: '⚡',
      title: 'After-Hours Capture',
      desc: 'Panic calls at 2 AM become organized, retained matters by 8 AM. Your paralegal costs drop, your intake revenue rises.',
    },
    {
      icon: '🏛️',
      title: 'Compliance First',
      desc: 'Pursuing SOC 2 Type II certification. HIPAA-supportive architecture. Built to withstand judicial scrutiny on privilege claims.',
    },
    {
      icon: '📈',
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
            <div key={f.title} className="glass-card">
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

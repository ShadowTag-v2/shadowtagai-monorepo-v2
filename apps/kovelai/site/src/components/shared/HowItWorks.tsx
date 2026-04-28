export default function HowItWorks() {
  const steps = [
    {
      num: '01',
      title: 'Client Logs In',
      desc: "Your client uses their credit card to access CounselConduit through your firm's branded portal. The card serves as both authentication and automated billing — no invoicing headaches.",
    },
    {
      num: '02',
      title: 'Client Searches Freely',
      desc: 'Web searches, AI queries, legal research — all routed through a privilege-protected connection to your firm. Your client relaxes, recalls facts, and explores their case without creating discoverable evidence.',
    },
    {
      num: '03',
      title: 'Attorney Monitors & Strategizes',
      desc: 'You see every search, every AI response, every session in real time. You give the first legal opinion — not the other side. You bill at the end of the cycle, in full compliance with professional responsibility rules.',
    },
  ];

  return (
    <section className="py-20 md:py-28" id="how-it-works">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">How CounselConduit Works</div>
        <h2 className="section-title">Three Steps. Full Privilege. Full Visibility.</h2>
        <div className="grid md:grid-cols-3 gap-8 mt-10">
          {steps.map((s) => (
            <div key={s.num} className="glass-card text-center">
              <div className="text-5xl font-extrabold text-gold leading-none mb-4">{s.num}</div>
              <h3 className="text-lg font-semibold text-primary-text mb-2">{s.title}</h3>
              <p className="text-sm leading-relaxed text-secondary-text">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

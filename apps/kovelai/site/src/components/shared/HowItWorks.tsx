export default function HowItWorks() {
  const steps = [
    {
      num: '01',
      title: 'Client Gets Secure Access',
      desc: "Your client logs into CounselConduit through your firm's branded portal using their credit card — which serves as both authentication and automated payment. They're instantly connected to a privilege-protected research environment.",
    },
    {
      num: '02',
      title: 'Client Searches Freely',
      desc: 'Web searches, AI queries, legal research — all routed through a secure connection to your firm. Your client searches whenever anxiety strikes. They relax, recall all the facts of their case, and explore their concerns — without creating discoverable evidence for the other side.',
    },
    {
      num: '03',
      title: 'Attorney Monitors & Bills',
      desc: 'You sit in the loop on every session. You see what your clients are searching and what AI responses they receive — in real time. You give the first legal opinion, not the other side. Their credit card is billed at the end of each cycle, in full compliance with the Rules of Professional Responsibility.',
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

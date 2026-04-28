export default function HowItWorks() {
  const steps = [
    {
      num: '01',
      title: 'You Buy It for Your Client',
      desc: "You purchase KovelAI as privileged infrastructure for your clients — like a police chief buying bulletproof vests for the force. You set the session rate, configure the portal, and onboard your client. It's their secure research environment, connected directly to your firm.",
    },
    {
      num: '02',
      title: 'Client Logs In, Searches Freely',
      desc: 'Your client logs in with their credit card — which serves as both authentication and automatic payment. They search the web, use AI, access translation and transcription tools, all routed through your privilege umbrella. They search whenever anxiety strikes, relax enough to recall all the facts of their case, and stop sending you random discoverable AI opinions at 2 AM.',
    },
    {
      num: '03',
      title: 'You Monitor, Opine, and Bill',
      desc: 'You sit in the loop on the entire cycle. You see every search, every AI query, every session — in real time. You give the first legal opinion instead of being surprised by what the client found on their own. Their credit card is billed at the end of each cycle, in full compliance with the Rules of Professional Responsibility. The privilege holds. The other side gets nothing.',
    },
  ];

  return (
    <section className="py-20 md:py-28" id="how-it-works">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">The Heppner Ultimatum — How It Works</div>
        <h2 className="section-title">
          Deploy the Portal. Monitor the Client. Bill Automatically.
        </h2>
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

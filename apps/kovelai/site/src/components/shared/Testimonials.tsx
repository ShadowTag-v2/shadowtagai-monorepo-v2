export default function Testimonials() {
  const testimonials = [
    {
      initials: 'MR',
      name: 'Managing Partner',
      firm: 'Am Law 200 Litigation Practice, New York',
      quote: `"After Heppner, the pitch to clients is simple: 'Either you search through our firm's KovelAI, or the other side gets everything.' We deployed it for our top clients — they search freely, we see everything, and the privilege holds. One client's protected search history would have been devastating if it had been discoverable."`,
    },
    {
      initials: 'SK',
      name: 'Senior Associate',
      firm: 'Boutique Family Law, Los Angeles',
      quote: `"Our custody clients used to text us random AI legal opinions at 2 AM — wrong, irritating, and discoverable. Now they search through our portal whenever anxiety strikes. They relax, recall facts, and I see exactly what they're worried about before court. No more surprises. I give the first opinion, not ChatGPT."`,
    },
    {
      initials: 'JL',
      name: 'Founding Partner',
      firm: 'Criminal Defense, Chicago',
      quote: `"We deploy KovelAI as privileged infrastructure for every active case. Clients log in with their credit card, and we monitor every session. I'm in the oversight seat on all case-related research. The billing is automatic. Intake revenue is up 40% since we deployed it."`,
    },
  ];

  return (
    <section className="py-20 md:py-28 bg-surface-lowest" id="testimonials">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">From the Bar</div>
        <h2 className="section-title">What Attorneys Are Saying</h2>
        <div className="grid md:grid-cols-3 gap-6 mt-10">
          {testimonials.map((t) => (
            <div key={t.initials} className="testimonial-card">
              <div className="testimonial-stars">★★★★★</div>
              <blockquote className="testimonial-quote">{t.quote}</blockquote>
              <div className="flex items-center gap-3 mt-auto">
                <div className="testimonial-avatar">{t.initials}</div>
                <div>
                  <div className="text-sm font-medium text-primary-text">{t.name}</div>
                  <div className="text-xs text-[#998f81]">{t.firm}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

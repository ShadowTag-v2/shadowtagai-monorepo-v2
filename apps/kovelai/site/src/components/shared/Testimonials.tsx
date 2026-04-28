export default function Testimonials() {
  const testimonials = [
    {
      initials: 'MR',
      name: 'Managing Partner',
      firm: 'Am Law 200 Litigation Practice, New York',
      quote: `"A client's Google search history was subpoenaed mid-litigation. After Heppner, we moved all client research to CounselConduit. The client felt safe searching again — and the privilege held. That one save paid for three years of service."`,
    },
    {
      initials: 'SK',
      name: 'Senior Associate',
      firm: 'Boutique Family Law, Los Angeles',
      quote: `"Our high-conflict custody clients used to text us panic searches at 2 AM. Now they search through CounselConduit whenever anxiety strikes — they relax, recall facts, and I can see exactly what they're worried about before we walk into court. No more ambushes."`,
    },
    {
      initials: 'JL',
      name: 'Founding Partner',
      firm: 'Criminal Defense, Chicago',
      quote: `"Our clients understand the Heppner risk — they're happy to pay for protection. Their credit card gets charged automatically, I see their searches in real time, and I give the first legal opinion. Intake revenue is up 40% since launch."`,
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

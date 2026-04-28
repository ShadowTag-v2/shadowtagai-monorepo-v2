export default function Testimonials() {
  const testimonials = [
    {
      initials: 'MR',
      name: 'Managing Partner',
      firm: 'Am Law 200 Litigation Practice, New York',
      quote:
        '"We had a client whose Google search history was subpoenaed mid-litigation. After Heppner, we moved all client research to KovelAI. The privilege held. That one save paid for three years of service."',
    },
    {
      initials: 'SK',
      name: 'Senior Associate',
      firm: 'Boutique Family Law, Los Angeles',
      quote:
        '"We deployed CounselConduit for our high-conflict custody clients. They search at all hours — nights, weekends, panic before hearings. Now every search is privileged, and I see exactly what they\'re worried about before we walk into court."',
    },
    {
      initials: 'JL',
      name: 'Founding Partner',
      firm: 'Criminal Defense, Chicago',
      quote:
        '"We bill clients $250/month for privileged search access. They\'re happy to pay because they understand the Heppner risk. Our intake revenue is up 40% since launch."',
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

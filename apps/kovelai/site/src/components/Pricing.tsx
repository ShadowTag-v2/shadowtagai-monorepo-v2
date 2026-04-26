'use client';

export default function Pricing() {
  const plans = [
    {
      tier: 'Trial',
      price: '0',
      period: '/mo',
      features: [
        '10,000 tokens/month',
        'Kovel Doctrine protection',
        'Zero data retention',
        'Basic intake dashboard',
        'Email support',
      ],
      cta: 'Start Free Trial',
      ctaLink: 'https://buy.stripe.com/test_aEU5nR1Jy9Mg8zS000',
      ctaStyle: 'btn-ghost',
      featured: false,
    },
    {
      tier: 'Professional',
      price: '149',
      period: '/mo',
      features: [
        '100,000 tokens/month',
        'Everything in Trial, plus:',
        'Privileged web search proxy',
        'After-hours AI intake',
        'Revenue analytics dashboard',
        'Matter pipeline integration',
        'Priority support',
      ],
      cta: 'Subscribe — $149/mo',
      ctaLink: '#',
      ctaStyle: 'btn-gold',
      featured: true,
      annual: 'or $1,428/yr (save $360)',
    },
    {
      tier: 'Enterprise',
      price: '20K',
      period: '/mo',
      features: [
        'Unlimited tokens',
        'Everything in Professional, plus:',
        'Dedicated compliance officer',
        'Custom retention policies',
        'BYOK (Bring Your Own Key)',
        'Regional data isolation',
        '24/7 phone + Slack support',
      ],
      cta: 'Contact Sales',
      ctaAction: true,
      ctaStyle: 'btn-ghost',
      featured: false,
    },
  ];

  const openModal = () => {
    document.getElementById('contactModal')?.classList.add('modal-overlay--visible');
  };

  return (
    <section className="py-20 md:py-28 bg-surface-lowest" id="pricing">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">Pricing</div>
        <h2 className="section-title">Simple, Transparent Pricing</h2>
        <p className="section-desc mb-12">
          Every plan includes Kovel Doctrine privilege protection, zero data retention, and Judge 6
          compliance governance.
        </p>
        <div className="grid md:grid-cols-3 gap-6">
          {plans.map((p) => (
            <div
              key={p.tier}
              className={`pricing-card ${p.featured ? 'pricing-card--featured' : ''}`}
            >
              {p.featured && <div className="pricing-badge">Most Popular</div>}
              <div className="text-xs uppercase tracking-[0.05em] text-[#998f81] mb-2">
                {p.tier}
              </div>
              <div className="text-3xl font-extrabold text-primary-text mb-4">
                <span className="text-lg text-[#998f81]">$</span>
                {p.price}
                <span className="text-sm font-normal text-[#998f81]">{p.period}</span>
              </div>
              <ul className="flex-1 space-y-2 mb-6">
                {p.features.map((f) => (
                  <li key={f} className="text-sm text-secondary-text flex items-start gap-2">
                    <span className="text-gold mt-0.5 text-xs">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
              {p.ctaAction ? (
                <button onClick={openModal} className={`${p.ctaStyle} w-full justify-center text-sm`}>
                  {p.cta}
                </button>
              ) : (
                <a href={p.ctaLink} className={`${p.ctaStyle} w-full justify-center text-sm`}>
                  {p.cta}
                </a>
              )}
              {p.annual && (
                <p className="text-xs text-center text-[#998f81] mt-2">{p.annual}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

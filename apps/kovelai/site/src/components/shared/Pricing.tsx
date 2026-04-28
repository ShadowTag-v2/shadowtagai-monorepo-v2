'use client';

/**
 * Stripe Integration Reference (DO NOT DELETE):
 * - Account: acct_1Syh9JEHnWpykeMi
 * - Pro Monthly Price ID: price_1TNKSREHnWpykeMiRMDlVgLl ($149/mo)
 * - Pro Annual Price ID: price_1TNKSjEHnWpykeMi0S9GCVjy ($1,428/yr)
 * - Enterprise Price ID: price_1TNKSREHnWpykeMi8mrDf4rI ($20K/mo)
 * - Beta Coupon Code: 3wseBY7Z (50% off, 3 months, max 100 redemptions)
 * - Customer Portal: bpc_1TNKSjEHnWpykeMi0qQPoaHm
 *
 * STRIPE CUTOVER STATUS (2026-04-28):
 * Live Payment Links wired. Trial → contact modal (qualification).
 * Pro Monthly/Annual → Stripe Checkout with beta coupon auto-applied.
 * Enterprise → contact modal (high-touch sales).
 */

interface PricingProps {
  onOpenModal: () => void;
}

/**
 * Stripe Checkout URLs with coupon pre-applied.
 * These use Stripe's `prefilled_promo_code` parameter to auto-fill 3wseBY7Z.
 * If the user creates dedicated Payment Links in the Dashboard, replace these
 * with the Payment Link URLs instead.
 */
const STRIPE_CHECKOUT = {
  proMonthly: `https://buy.stripe.com/live_pro_monthly?prefilled_promo_code=3wseBY7Z`,
  proAnnual: `https://buy.stripe.com/live_pro_annual`,
} as const;

export default function Pricing({ onOpenModal }: PricingProps) {
  const plans = [
    {
      tier: 'Trial',
      price: '0',
      period: '/mo',
      features: [
        '10,000 tokens/month',
        'Kovel Doctrine protection',
        'Zero data retention',
        'Branded client portal',
        'Email support',
      ],
      cta: 'Start Free Trial',
      ctaLink: null as string | null,
      ctaStyle: 'btn-ghost',
      featured: false,
    },
    {
      tier: 'Professional',
      price: '149',
      period: '/mo',
      badge: '50% OFF — Beta Launch',
      features: [
        '100,000 tokens/month',
        'Everything in Trial, plus:',
        'Privileged web search proxy',
        'Attorney monitoring dashboard',
        'Revenue analytics dashboard',
        'Client session archive',
        'Priority support',
      ],
      cta: 'Start Pro — $74.50/mo',
      ctaLink: STRIPE_CHECKOUT.proMonthly,
      ctaStyle: 'btn-gold',
      featured: true,
      annual: {
        label: 'or $1,428/yr (save $360)',
        link: STRIPE_CHECKOUT.proAnnual,
      },
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
      ctaLink: null as string | null,
      ctaStyle: 'btn-ghost',
      featured: false,
    },
  ];

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
              {p.badge && (
                <div className="text-[0.65rem] uppercase tracking-[0.15em] text-gold font-semibold mb-1">
                  {p.badge}
                </div>
              )}
              <div className="text-xs uppercase tracking-[0.05em] text-[#a89d8e] mb-2">
                {p.tier}
              </div>
              <div className="text-3xl font-extrabold text-primary-text mb-4">
                <span className="text-lg text-[#a89d8e]">$</span>
                {p.price}
                <span className="text-sm font-normal text-[#a89d8e]">{p.period}</span>
              </div>
              <ul className="flex-1 space-y-2 mb-6">
                {p.features.map((f) => (
                  <li key={f} className="text-sm text-secondary-text flex items-start gap-2">
                    <span className="text-gold mt-0.5 text-xs">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
              {p.ctaLink ? (
                <a
                  href={p.ctaLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`${p.ctaStyle} w-full justify-center text-sm inline-flex items-center`}
                  id={`cta-${p.tier.toLowerCase()}`}
                >
                  {p.cta}
                </a>
              ) : (
                <button
                  type="button"
                  onClick={onOpenModal}
                  className={`${p.ctaStyle} w-full justify-center text-sm`}
                  id={`cta-${p.tier.toLowerCase()}`}
                >
                  {p.cta}
                </button>
              )}
              {p.annual && (
                <p className="text-xs text-center text-[#a89d8e] mt-2">
                  <a
                    href={p.annual.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline decoration-dotted underline-offset-2 hover:text-gold transition-colors"
                  >
                    {p.annual.label}
                  </a>
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

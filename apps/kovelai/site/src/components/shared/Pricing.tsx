'use client';

import { useState } from 'react';

/**
 * Stripe Integration Reference (DO NOT DELETE):
 * - Account: acct_1Syh9JEHnWpykeMi
 * - Pro Monthly Price ID: price_1TNKSREHnWpykeMiRMDlVgLl ($149/mo)
 * - Pro Annual Price ID: price_1TNKSjEHnWpykeMi0S9GCVjy ($1,428/yr)
 * - Enterprise Price ID: price_1TNKSREHnWpykeMi8mrDf4rI ($20K/mo)
 * - Beta Coupon Code: 3wseBY7Z (50% off, 3 months, max 100 redemptions)
 * - Customer Portal: bpc_1TNKSjEHnWpykeMi0qQPoaHm
 *
 * Payment Link Integration:
 * - Trial CTA reads from NEXT_PUBLIC_STRIPE_TRIAL_LINK env var.
 * - Pro Monthly CTA reads from NEXT_PUBLIC_STRIPE_PRO_MONTHLY_LINK env var.
 * - Pro Annual CTA reads from NEXT_PUBLIC_STRIPE_PRO_ANNUAL_LINK env var.
 * - Enterprise routes through the contact modal (onOpenModal).
 * - To activate: Create Payment Links in Stripe Dashboard → set env vars → redeploy.
 * - Checkout API alternative: /api/billing/checkout (server-side Stripe Checkout Session).
 */

const TRIAL_LINK = process.env.NEXT_PUBLIC_STRIPE_TRIAL_LINK || '#';
const PRO_MONTHLY_LINK =
  process.env.NEXT_PUBLIC_STRIPE_PRO_MONTHLY_LINK || process.env.NEXT_PUBLIC_STRIPE_PRO_LINK || '#';
const PRO_ANNUAL_LINK = process.env.NEXT_PUBLIC_STRIPE_PRO_ANNUAL_LINK || '#';

interface PricingProps {
  onOpenModal: () => void;
}

export default function Pricing({ onOpenModal }: PricingProps) {
  const [isAnnual, setIsAnnual] = useState(false);

  const proPrice = isAnnual ? '119' : '149';
  const proPeriod = '/mo';
  const proCtaLabel = isAnnual ? 'Start Pro — $59.50/mo' : 'Start Pro — $74.50/mo';
  const proCtaLink = isAnnual ? PRO_ANNUAL_LINK : PRO_MONTHLY_LINK;
  const proSubtext = isAnnual
    ? 'Billed $1,428/yr — save $360 vs monthly'
    : 'or save 20% with annual billing →';

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
      ctaLink: TRIAL_LINK,
      ctaStyle: 'btn-ghost',
      featured: false,
    },
    {
      tier: 'Professional',
      price: proPrice,
      period: proPeriod,
      badge: '50% OFF — Beta Launch',
      features: [
        '100,000 tokens/month',
        'Everything in Trial, plus:',
        'Privileged web search proxy',
        'After-hours AI intake',
        'Revenue analytics dashboard',
        'Matter pipeline integration',
        'Priority support',
      ],
      cta: proCtaLabel,
      ctaLink: proCtaLink,
      ctaStyle: 'btn-gold',
      featured: true,
      subtext: proSubtext,
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

  return (
    <section className="py-20 md:py-28 bg-surface-lowest" id="pricing">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">Pricing</div>
        <h2 className="section-title">Simple, Transparent Pricing</h2>
        <p className="section-desc mb-8">
          Every plan includes Kovel Doctrine privilege protection, zero data retention, and Judge 6
          compliance governance.
        </p>

        {/* Monthly / Annual Toggle */}
        <div className="flex items-center justify-center gap-3 mb-12">
          <button
            id="monthly-btn"
            type="button"
            onClick={() => setIsAnnual(false)}
            className={`text-sm font-medium transition-colors ${!isAnnual ? 'text-primary-text' : 'text-[#998f81]'}`}
          >
            Monthly
          </button>
          <button
            type="button"
            role="switch"
            aria-checked={isAnnual}
            aria-label="Toggle annual billing"
            onClick={() => setIsAnnual(!isAnnual)}
            className="relative inline-flex h-7 w-[52px] shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold focus-visible:ring-offset-2 focus-visible:ring-offset-[#071325]"
            style={{
              backgroundColor: isAnnual ? '#e6c487' : 'rgba(77,70,58,0.3)',
            }}
          >
            <span
              className="pointer-events-none inline-block h-[22px] w-[22px] rounded-full bg-white shadow-lg ring-0 transition-transform duration-200 ease-in-out"
              style={{
                transform: isAnnual ? 'translateX(26px)' : 'translateX(2px)',
                marginTop: '1px',
              }}
            />
          </button>
          <button
            id="annual-btn"
            type="button"
            onClick={() => setIsAnnual(true)}
            className={`text-sm font-medium transition-colors ${isAnnual ? 'text-primary-text' : 'text-[#998f81]'}`}
          >
            Annual
          </button>
          {isAnnual && (
            <span className="ml-1 inline-flex items-center rounded-full bg-gold/15 px-2.5 py-0.5 text-[0.65rem] font-semibold text-gold uppercase tracking-wider animate-pulse">
              Save 20%
            </span>
          )}
        </div>

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
              <div className="tier-name text-xs uppercase tracking-[0.05em] text-[#a89d8e] mb-2">
                {p.tier}
              </div>
              <div className="text-3xl font-extrabold text-primary-text mb-4">
                <span className="text-lg text-[#a89d8e]">$</span>
                <span id={p.tier === 'Professional' ? 'pro-price' : undefined}>{p.price}</span>
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
              {p.ctaAction ? (
                <button
                  type="button"
                  onClick={onOpenModal}
                  className={`cta-btn ${p.ctaStyle} w-full justify-center text-sm`}
                >
                  {p.cta}
                </button>
              ) : (
                <a href={p.ctaLink} className={`cta-btn ${p.ctaStyle} w-full justify-center text-sm`}>
                  {p.cta}
                </a>
              )}
              {p.subtext && <p className="text-xs text-center text-[#a89d8e] mt-2">{p.subtext}</p>}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

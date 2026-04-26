/**
 * Pricing domain types — extracted from Pricing.tsx inline definitions.
 */

export interface PricingFeature {
  text: string;
  included: boolean;
}

export interface PricingPlan {
  name: string;
  price: string;
  period: string;
  description: string;
  features: PricingFeature[];
  ctaLabel: string;
  /** External payment link URL (Stripe Payment Links). */
  ctaLink?: string;
  /** If true, CTA opens the contact modal instead of navigating. */
  ctaAction?: boolean;
  highlighted?: boolean;
  badge?: string;
}

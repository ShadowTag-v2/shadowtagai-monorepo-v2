/**
 * V23 Pomelli Swarm Target Matrix
 * Defines the 3 live properties for autonomous web auditing.
 */

export interface SwarmTarget {
  id: string;
  url: string;
  kpi: string;
  platform: "Firebase Hosting" | "Cloud Run";
  lighthouseBaseline: {
    performance: number;
    accessibility: number;
    bestPractices: number;
    seo: number;
  };
}

export const POMELLI_TARGET_MATRIX: SwarmTarget[] = [
  {
    id: "headfade-marketing",
    url: "https://headfade.com",
    kpi: "Maintain P100/A100/BP100/SEO100 Lighthouse hegemony",
    platform: "Firebase Hosting",
    lighthouseBaseline: {
      performance: 100,
      accessibility: 100,
      bestPractices: 100,
      seo: 100,
    },
  },
  {
    id: "counselconduit-app",
    url: "https://counselconduit-767252945109.us-central1.run.app",
    kpi: "Stripe Checkout Conversion Rate & TTI",
    platform: "Cloud Run",
    lighthouseBaseline: {
      performance: 94,
      accessibility: 93,
      bestPractices: 100,
      seo: 100,
    },
  },
  {
    id: "shadowtagai-dashboard",
    url: "https://shadowtagai.web.app",
    kpi: "Visual Provenance & AST Integrity",
    platform: "Firebase Hosting",
    lighthouseBaseline: {
      performance: 94,
      accessibility: 93,
      bestPractices: 100,
      seo: 100,
    },
  },
];

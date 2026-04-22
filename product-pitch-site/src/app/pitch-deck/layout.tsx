import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "KovelAI Investor Pitch Deck | Post-Heppner Privileged Client AI",
  description:
    "Confidential pre-seed pitch deck for KovelAI — the Shopify for Legal AI. Privileged, prepaid, client-facing AI portals for law firms. $500B+ market opportunity.",
  openGraph: {
    title: "KovelAI Investor Pitch Deck",
    description:
      "Post-Heppner Privileged Client AI. The only platform where clients get AI and lawyers get paid.",
    type: "website",
    siteName: "KovelAI",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "KovelAI Pitch Deck",
    description:
      "Post-Heppner Privileged Client AI. Antigravity for the Practice of Law.",
  },
  robots: {
    index: false,
    follow: false,
  },
};

export default function PitchDeckLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

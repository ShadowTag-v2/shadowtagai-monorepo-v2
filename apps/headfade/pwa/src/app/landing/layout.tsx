import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'HeadFade — The Truth Layer for the Synthetic Internet',
  description:
    'HeadFade is forensic infrastructure for detecting AI-generated media. Four AI agents analyze every frame in parallel under 300ms. Publishers embed trust scores. Creators monetize authenticity.',
  openGraph: {
    title: 'HeadFade — The Truth Layer for the Synthetic Internet',
    description:
      'Forensic AI detection infrastructure. Four agents. Sub-300ms verdicts. The Human Deception Index.',
    type: 'website',
    url: 'https://headfade.com/landing',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'HeadFade — Forensic AI Detection',
    description:
      "Can you tell what's real? Join millions training the world's most advanced deepfake detection engine.",
  },
};

export default function LandingLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Trust & Security | KovelAI',
  description:
    'KovelAI security architecture, compliance certifications, and privilege-preservation guarantees. SOC 2 Type II certified. Heppner-compliant by design.',
  openGraph: {
    title: 'Trust & Security | KovelAI',
    description:
      'KovelAI security architecture, compliance certifications, and privilege-preservation guarantees.',
    type: 'website',
  },
};

export default function TrustLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

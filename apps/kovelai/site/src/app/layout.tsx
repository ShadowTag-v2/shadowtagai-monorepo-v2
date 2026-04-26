import type { Metadata } from 'next';
import { Inter, Geist_Mono } from 'next/font/google';
import './globals.css';

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  display: 'optional',
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'KovelAI | Post-Heppner Privileged Client AI and Web Search Through Your Firm',
  description:
    'KovelAI protects post-Heppner client internet searches from discovery while helping law firms get paid on the front end. Secure AI intake, after-hours capture, and revenue acceleration for modern practices.',
  metadataBase: new URL('https://kovelai.com'),
  openGraph: {
    type: 'website',
    url: 'https://kovelai.com/',
    title: 'KovelAI | Post-Heppner Privileged Client AI',
    description:
      'KovelAI protects post-Heppner client internet searches from discovery while helping law firms get paid on the front end.',
    siteName: 'KovelAI',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'KovelAI | Post-Heppner Privileged Client AI',
    description:
      'KovelAI protects post-Heppner client internet searches from discovery while helping law firms get paid on the front end.',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large' as const,
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/favicon.ico',
  },
  manifest: '/manifest.json',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${geistMono.variable} antialiased`}>
      <head>
        <link rel="canonical" href="https://kovelai.com/" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@graph': [
                {
                  '@type': 'Organization',
                  '@id': 'https://kovelai.com/#organization',
                  name: 'KovelAI',
                  url: 'https://kovelai.com/',
                  description:
                    'KovelAI protects post-Heppner client internet searches from discovery while helping law firms get paid on the front end.',
                  foundingDate: '2024',
                },
                {
                  '@type': 'WebSite',
                  '@id': 'https://kovelai.com/#website',
                  url: 'https://kovelai.com/',
                  name: 'KovelAI',
                  publisher: { '@id': 'https://kovelai.com/#organization' },
                  inLanguage: 'en-US',
                },
                {
                  '@type': 'SoftwareApplication',
                  name: 'KovelAI',
                  applicationCategory: 'LegalService',
                  operatingSystem: 'Web',
                  offers: [
                    { '@type': 'Offer', price: '0', priceCurrency: 'USD', description: 'Trial — 10,000 tokens/month' },
                    {
                      '@type': 'Offer',
                      price: '149',
                      priceCurrency: 'USD',
                      description: 'Professional — 100,000 tokens/month',
                    },
                    {
                      '@type': 'Offer',
                      price: '20000',
                      priceCurrency: 'USD',
                      description: 'Enterprise — Unlimited',
                    },
                  ],
                },
              ],
            }),
          }}
        />
      </head>
      <body className="min-h-screen flex flex-col bg-[#071325] text-[#d7e3fc]">{children}</body>
    </html>
  );
}

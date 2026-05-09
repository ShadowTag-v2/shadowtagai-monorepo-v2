import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import type React from 'react';
import './globals.css';
import { ServiceWorkerRegistrar } from './sw-register';

const inter = Inter({ subsets: ['latin'] });

export const viewport: Viewport = {
  themeColor: '#06b6d4',
  colorScheme: 'dark',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
};

export const metadata: Metadata = {
  title: 'HeadFade | Global Synthetic Media Infrastructure',
  description:
    "The world's first forensic deepfake detection platform. Embed player, creator marketplace, and cognitive telemetry — powered by Gemini AI.",
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'HeadFade',
  },
  openGraph: {
    title: 'HeadFade — Synthetic Media Infrastructure',
    description:
      'Forensic deepfake detection, embeddable players for publishers, and a micro-licensing marketplace for AI creators. Powered by Gemini 3.1.',
    url: 'https://headfade.web.app',
    siteName: 'HeadFade',
    locale: 'en_US',
    type: 'website',
    images: [
      {
        url: 'https://headfade.web.app/og-image.png',
        width: 1200,
        height: 630,
        alt: 'HeadFade — Forensic Deepfake Infrastructure',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'HeadFade — Synthetic Media Infrastructure',
    description:
      'Forensic detection. Creator marketplace. Embed distribution. Powered by Gemini AI.',
    images: ['https://headfade.web.app/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    },
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        {/* Performance: DNS prefetch + preconnect for external origins */}
        <link rel="dns-prefetch" href="https://images.unsplash.com" />
        <link rel="dns-prefetch" href="https://fonts.googleapis.com" />
        <link rel="dns-prefetch" href="https://www.googletagmanager.com" />
        <link rel="preconnect" href="https://images.unsplash.com" crossOrigin="anonymous" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        {/* LCP: Preload hero carousel image — first SEED_VIDEO thumbnail */}
        <link
          rel="preload"
          as="image"
          href="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600&h=340&fit=crop"
          fetchPriority="high"
        />
        <link rel="icon" href="/icons/icon-192.png" type="image/png" />
        <link rel="apple-touch-icon" href="/icons/icon-192.png" />
      </head>
      <body className={`${inter.className} bg-black text-white antialiased`}>
        {children}
        <ServiceWorkerRegistrar />
      </body>
    </html>
  );
}

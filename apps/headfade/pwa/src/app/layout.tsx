import type { Metadata, Viewport } from 'next';
import React from 'react';
import { Inter } from 'next/font/google';
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
  title: 'HeadFadeAi | Gamified Turing Test',
  description:
    'Can you tell what is real? The world\'s first gamified deepfake detection platform powered by Gemini AI.',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'HeadFadeAi',
  },
  openGraph: {
    title: 'HeadFadeAi — The Global Turing Test',
    description:
      'Swipe through AI-generated and real videos. Can you tell the difference? Powered by Gemini 3.1 Flash Lite forensics.',
    url: 'https://headfade.web.app',
    siteName: 'HeadFadeAi',
    locale: 'en_US',
    type: 'website',
    images: [
      {
        url: 'https://headfade.web.app/og-image.png',
        width: 1200,
        height: 630,
        alt: 'HeadFadeAi — Can you tell what is real?',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'HeadFadeAi — The Global Turing Test',
    description: 'Swipe. Vote. Discover. Powered by Gemini AI forensics.',
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

import type { Metadata } from "next";
import { Geist_Mono, Inter } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import "./agent-spinner.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  display: "optional",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "KovelAI | Post-Heppner Privileged Client AI and Web Search Through Your Firm",
  description:
    "KovelAI protects post-Heppner client internet searches from discovery while helping law firms get paid on the front end. Secure AI intake, after-hours capture, and revenue acceleration for modern practices.",
  metadataBase: new URL("https://kovelai.com"),
  openGraph: {
    type: "website",
    url: "https://kovelai.com/",
    title: "KovelAI | Post-Heppner Privileged Client AI",
    description:
      "KovelAI protects post-Heppner client internet searches from discovery while helping law firms get paid on the front end.",
    siteName: "KovelAI",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "KovelAI | Post-Heppner Privileged Client AI",
    description:
      "KovelAI protects post-Heppner client internet searches from discovery while helping law firms get paid on the front end.",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large" as const,
      "max-snippet": -1,
    },
  },
  icons: {
    icon: [
      { url: "/favicon-32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-64.png", sizes: "64x64", type: "image/png" },
    ],
    apple: "/apple-touch-icon.png",
  },
  manifest: "/manifest.json",
};

/**
 * Static export layout — CSP is enforced via firebase.json response headers.
 * Nonce injection requires SSR (headers() is incompatible with output: 'export').
 * When migrating to SSR in the future, restore middleware.ts + headers() nonce flow.
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${geistMono.variable} antialiased`}>
      <head>
        {process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID && (
          <>
            <Script
              id="ga4-gtag"
              strategy="afterInteractive"
              src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}`}
            />
            <Script
              id="ga4-config"
              strategy="afterInteractive"
              // biome-ignore lint/security/noDangerouslySetInnerHtml: GA4 analytics config — controlled server-rendered snippet
              dangerouslySetInnerHTML={{
                __html: `
                  window.dataLayer = window.dataLayer || [];
                  function gtag(){dataLayer.push(arguments);}
                  gtag('js', new Date());
                  gtag('config', '${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}', {
                    page_path: window.location.pathname,
                    send_page_view: true
                  });
                `,
              }}
            />
          </>
        )}
        <link rel="canonical" href="https://kovelai.com/" />
        <script
          type="application/ld+json"
          // biome-ignore lint/security/noDangerouslySetInnerHtml: LD+JSON structured data — static server-rendered SEO markup, not executable
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@graph": [
                {
                  "@type": "Organization",
                  "@id": "https://kovelai.com/#organization",
                  name: "KovelAI",
                  url: "https://kovelai.com/",
                  description:
                    "KovelAI protects post-Heppner client internet searches from discovery while helping law firms get paid on the front end.",
                  foundingDate: "2024",
                },
                {
                  "@type": "WebSite",
                  "@id": "https://kovelai.com/#website",
                  url: "https://kovelai.com/",
                  name: "KovelAI",
                  publisher: { "@id": "https://kovelai.com/#organization" },
                  inLanguage: "en-US",
                },
                {
                  "@type": "SoftwareApplication",
                  name: "KovelAI",
                  applicationCategory: "LegalService",
                  operatingSystem: "Web",
                  offers: [
                    {
                      "@type": "Offer",
                      price: "0",
                      priceCurrency: "USD",
                      description: "Trial — 10,000 tokens/month",
                    },
                    {
                      "@type": "Offer",
                      price: "149",
                      priceCurrency: "USD",
                      description: "Professional — 100,000 tokens/month",
                    },
                    {
                      "@type": "Offer",
                      price: "20000",
                      priceCurrency: "USD",
                      description: "Enterprise — Unlimited",
                    },
                  ],
                },
                {
                  "@type": "FAQPage",
                  mainEntity: [
                    {
                      "@type": "Question",
                      name: "What is the Kovel Doctrine?",
                      acceptedAnswer: {
                        "@type": "Answer",
                        text: "The Kovel Doctrine (from United States v. Kovel, 296 F.2d 918) extends attorney-client privilege to non-attorney agents — like accountants, interpreters, or AI tools — working under the attorney's direction. KovelAI operates as a Kovel agent under your firm's privilege umbrella.",
                      },
                    },
                    {
                      "@type": "Question",
                      name: "Is my client data stored anywhere?",
                      acceptedAnswer: {
                        "@type": "Answer",
                        text: "No. KovelAI uses zero-retention architecture. All data is processed in RAM only and never written to disk. Session data is cryptographically shredded when the session ends.",
                      },
                    },
                    {
                      "@type": "Question",
                      name: "What happened in In re Heppner?",
                      acceptedAnswer: {
                        "@type": "Answer",
                        text: "In In re Heppner (S.D.N.Y., Feb. 10, 2026), the court ruled that client internet search histories conducted outside of attorney-supervised channels are discoverable in litigation. This created the post-Heppner compliance gap that KovelAI was built to fill.",
                      },
                    },
                    {
                      "@type": "Question",
                      name: "How does billing work for privileged sessions?",
                      acceptedAnswer: {
                        "@type": "Answer",
                        text: "Clients access KovelAI through your firm's branded portal. Each privileged session generates a billable entry. Most firms bill clients $50–$250 per session for privileged AI and web search access.",
                      },
                    },
                    {
                      "@type": "Question",
                      name: "What AI model does KovelAI use?",
                      acceptedAnswer: {
                        "@type": "Answer",
                        text: "KovelAI uses Google Gemini 2.5 Flash via Vertex AI, governed by the Judge 6 Compliance Framework. The model never trains on your data, and all inference happens within our zero-retention pipeline.",
                      },
                    },
                    {
                      "@type": "Question",
                      name: "Does KovelAI support SOC 2 / HIPAA-aligned practices?",
                      acceptedAnswer: {
                        "@type": "Answer",
                        text: "KovelAI is pursuing SOC 2 Type II certification. Our zero-retention architecture means no PHI is ever stored, providing a HIPAA-supportive foundation for healthcare law practices.",
                      },
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

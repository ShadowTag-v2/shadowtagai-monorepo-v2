import type { Metadata } from "next";
import Script from "next/script";
import { Inter } from "next/font/google";
import CookieConsent from "@/components/CookieConsent";
import ThemeToggle from "@/components/ThemeToggle";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800", "900"],
});

const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID || "";

/* Item 12: og:image social preview | Item 20: metadataBase for OG resolution */
export const metadata: Metadata = {
  metadataBase: new URL("https://kovelai.web.app"),
  title: "KovelAI | Post-Heppner Privileged Client AI and Web Search Through Your Firm, While You Get Paid",
  description:
    "The Shopify for Legal AI. Route client research through Gemini, Claude, ChatGPT & Google while preserving attorney-client privilege. Lawyers get paid per query.",
  keywords: [
    "legal AI",
    "attorney-client privilege",
    "Heppner",
    "Kovel doctrine",
    "AI legal research",
    "KovelAI",
    "CounselConduit",
  ],
  openGraph: {
    title: "KovelAI | Post-Heppner Privileged Client AI",
    description:
      "AI-powered legal research that keeps you privileged and paid.",
    type: "website",
    url: "https://kovelai.com",
    images: [
      {
        url: "https://kovelai.web.app/seo/og-image.png",
        width: 1200,
        height: 630,
        alt: "KovelAI — Privileged AI for Law Firms",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "KovelAI | Post-Heppner Privileged Client AI",
    description: "Route client AI research through your firm. Bill every query.",
    images: ["https://kovelai.web.app/seo/og-image.png"],
  },
};

/* Item 17: JSON-LD Structured Data for Legal SaaS */
const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "KovelAI",
  applicationCategory: "BusinessApplication",
  operatingSystem: "Web",
  description:
    "The Shopify for Legal AI. Privilege-preserving routing tier between law firms and foundational LLMs.",
  url: "https://kovelai.com",
  offers: [
    {
      "@type": "Offer",
      name: "Solo",
      price: "299",
      priceCurrency: "USD",
      priceSpecification: { "@type": "UnitPriceSpecification", billingDuration: "P1M" },
    },
    {
      "@type": "Offer",
      name: "Practice",
      price: "599",
      priceCurrency: "USD",
      priceSpecification: { "@type": "UnitPriceSpecification", billingDuration: "P1M" },
    },
    {
      "@type": "Offer",
      name: "Enterprise",
      price: "999",
      priceCurrency: "USD",
      priceSpecification: { "@type": "UnitPriceSpecification", billingDuration: "P1M" },
    },
  ],
  provider: {
    "@type": "Organization",
    name: "ShadowTag AI, Inc.",
    url: "https://shadowtagai.com",
    foundingDate: "2025",
    sameAs: ["https://kovelai.web.app"],
  },
  featureList: [
    "Attorney-client privilege preservation",
    "Multi-model AI routing (Gemini, Claude, ChatGPT, Google)",
    "Per-query billing",
    "Kovel attestation receipts",
    "SOC 2 Type II compliance",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} dark`}>
      <head>
        {/* Item 17: JSON-LD structured data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className="min-h-screen bg-[#0a0a0f] text-white font-[family-name:var(--font-inter)] antialiased">
        {children}
        {/* Item 16: GDPR cookie consent */}
        <CookieConsent />
        {/* Item 15: Dark/light mode toggle */}
        <ThemeToggle />
        {/* Google Analytics (item 6) */}
        {GA_MEASUREMENT_ID && (
          <>
            <Script
              src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`}
              strategy="afterInteractive"
            />
            <Script id="gtag-init" strategy="afterInteractive">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${GA_MEASUREMENT_ID}', {
                  page_path: window.location.pathname,
                });
              `}
            </Script>
          </>
        )}
      </body>
    </html>
  );
}

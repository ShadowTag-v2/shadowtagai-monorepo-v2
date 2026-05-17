// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * Root Layout — Global providers and meta configuration.
 *
 * Wires the PanopticonProvider at the root level so all pages
 * have access to unified telemetry via usePanopticonContext().
 *
 * Architecture:
 *   <html> → <body> → <PanopticonProvider> → {children}
 *
 * Security:
 *   - PII stripping handled inside PanopticonProvider
 *   - CSP headers set via firebase.json (not here)
 *   - No inline scripts (compliant with strict CSP)
 */

import type { Metadata } from "next";
import { PanopticonProvider } from "@/components/telemetry/PanopticonProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "CounselConduit — Privilege-Preserving Legal AI",
  description:
    "Secure AI-assisted document review for law firms. Attorney-monitored, privilege-preserving, Heppner-compliant.",
  robots: {
    index: false, // Legal SaaS — no public indexing
    follow: false,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <PanopticonProvider>{children}</PanopticonProvider>
      </body>
    </html>
  );
}

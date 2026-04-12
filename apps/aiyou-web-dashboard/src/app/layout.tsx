"use client";

import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import Image from "next/image";
import Link from "next/link";
import { CopilotKit } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ShadowTag - Serving the Global AI Industry",
  description: "Advanced Intelligence Matrices and Commercial AI Protocol Enforcement.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable} h-full antialiased`}>
      <body className="flex flex-col min-h-screen font-sans bg-white text-gray-900 relative">
        {/* Top Mini Nav */}
        <div className="bg-[#0B0A11] border-b border-gray-800 text-xs text-white flex justify-end items-center px-8 py-1.5 space-x-6 font-semibold tracking-wide border-opacity-70">
          <button type="button" className="hover:text-gray-300" aria-label="Decrease font size" onClick={() => { document.documentElement.style.fontSize = Math.max(12, parseFloat(getComputedStyle(document.documentElement).fontSize) - 2) + 'px'; }}>
            A-
          </button>
          <button type="button" className="hover:text-gray-300" aria-label="Increase font size" onClick={() => { document.documentElement.style.fontSize = Math.min(24, parseFloat(getComputedStyle(document.documentElement).fontSize) + 2) + 'px'; }}>
            A+
          </button>
          <button type="button" className="flex items-center hover:text-gray-300" aria-label="Toggle high contrast" onClick={() => { document.documentElement.classList.toggle('high-contrast'); }}>
            <svg
              className="w-3 h-3 mr-1"
              fill="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M12 2v20c5.523 0 10-4.477 10-10S17.523 2 12 2z" />
            </svg>
            Contrast
          </button>
          <button type="button" className="flex items-center hover:text-gray-300" aria-label="Open accessibility options" onClick={() => { document.querySelector('.fixed.bottom-6.left-6')?.scrollIntoView({ behavior: 'smooth' }); }}>
            <svg
              className="w-3 h-3 mr-1"
              fill="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v2m-2 4h4m-2 4v2" />
            </svg>
            Accessibility
          </button>
          <Link
            href="/contact/contact-sales-inquiries"
            className="border border-white hover:bg-white hover:text-black transition-colors rounded-full px-4 py-1.5 ml-4 text-xs font-bold uppercase"
          >
            Contact Sales
          </Link>
        </div>

        {/* Main Header Nav */}
        <header className="bg-[#0B0A11] text-white py-4 px-8 flex items-center justify-between sticky top-0 z-50 shadow-lg">
          <Link
            href="/"
            className="flex items-center space-x-3 group cursor-pointer hover:opacity-90 transition-opacity"
          >
            <div className="relative w-12 h-12 rounded-full overflow-hidden flex items-center justify-center bg-black shrink-0 border border-white/10 shadow-[0_0_15px_rgba(16,185,129,0.3)]">
              <Image
                src="/circuit-leaf-logo.jpg"
                alt="UphillSnowball Logo"
                fill
                className="object-cover scale-105"
              />
            </div>
            <div className="flex flex-col leading-[1.1] ml-1">
              <span className="text-[22px] font-inter font-black tracking-[-0.02em] text-white uppercase">
                UPHILLSNOWBALL
              </span>
              <span className="text-[10px] tracking-widest text-[#00b271] uppercase font-bold mt-0.5">
                BY SHADOWTAG AI
              </span>
            </div>
          </Link>
          <nav className="hidden md:flex space-x-8 text-sm font-bold uppercase font-inter items-center">
            <Link href="/products" className="hover:text-emerald-400 transition-colors">
              Products
            </Link>
            <Link href="/news-events/events" className="hover:text-emerald-400 transition-colors">
              Media & Events
            </Link>
            <a
              href="/shadowtag_investor_deck.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-emerald-400 transition-colors"
            >
              Investors
            </a>
            <Link href="/contact" className="hover:text-emerald-400 transition-colors">
              Contact
            </Link>
            <Link href="/careers" className="hover:text-emerald-400 transition-colors">
              Careers
            </Link>
            <Link href="/about-us" className="hover:text-emerald-400 transition-colors">
              About Us
            </Link>
          </nav>
        </header>

        {/* Main Content Area */}
        <main className="flex-grow w-full bg-white z-0">
          <CopilotKit runtimeUrl="/api/copilotkit" agent="shadowtag_nexus_agent">
            {children}
          </CopilotKit>
        </main>

        {/* Global Footer */}
        <footer className="bg-[#0B0A11] text-white flex flex-col items-center justify-between px-8 py-6 text-xs md:flex-row relative z-10 border-t border-gray-900 shadow-xl overflow-hidden">
          <div className="absolute inset-0 opacity-5 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-900 via-[#0B0A11] to-[#0B0A11]"></div>
          <div className="relative font-mono text-gray-400 mb-4 md:mb-0">
            ShadowTagAi - All Rights Reserved
          </div>
          <div className="relative flex space-x-6">
            <span
              className="text-gray-500 transition-colors cursor-not-allowed"
              aria-label="Social Link 1"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15h-2v-6h2v6zm-1-6.8c-.66 0-1.2-.54-1.2-1.2s.54-1.2 1.2-1.2 1.2.54 1.2 1.2-.54 1.2-1.2 1.2zm6.5 6.8h-2v-3.5c0-.83 0-1.9-.96-1.9-.96 0-1.11.75-1.11 1.84V17h-2v-6h2v.82h.03c.28-.53.96-1.08 1.97-1.08 2.11 0 2.5 1.39 2.5 3.2V17z" />
              </svg>
            </span>
            <Link
              href="https://x.com/ShadowTagAI"
              className="hover:text-emerald-400 transition-colors"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="X Profile"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z" />
              </svg>
            </Link>
          </div>
          <div className="relative text-gray-500 font-semibold mt-4 md:mt-0">Powered by MZ</div>
        </footer>

        {/* Sticky Accessibility Badge (Bottom Left) */}
        <div className="fixed bottom-6 left-6 z-50 cursor-pointer hover:scale-105 transition-transform bg-[#0B0A11] p-2 rounded-full border-2 border-[#3b3559] shadow-[0_0_15px_rgba(59,53,89,0.5)]">
          <svg
            className="w-8 h-8 text-white"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 6v2m-3 4h6m-3-4v8m-2 4h4"></path>
          </svg>
        </div>

        {/* Sticky reCAPTCHA Badge (Bottom Right) */}
        <div className="fixed bottom-6 right-6 z-50 bg-white border border-gray-200 shadow-md p-2 rounded-md flex flex-col items-center hover:opacity-100 opacity-90 transition-opacity cursor-pointer w-[72px]">
          <div className="flex flex-col items-center justify-between h-full w-full">
            <div className="relative w-8 h-8 mb-1">
              <svg
                viewBox="0 0 32 32"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="w-full h-full"
                aria-hidden="true"
              >
                <path
                  d="M16 28C14.4241 28 12.8637 27.6896 11.4078 27.0866C9.95189 26.4835 8.62902 25.5996 7.51472 24.4853L4.68629 27.3137C6.18664 28.8141 7.99496 29.9333 9.98808 30.7072C11.9812 31.481 14.1128 31.8906 16.2731 31.9161C18.4334 31.9416 20.5739 31.5822 22.5831 30.857C24.5923 30.1318 26.4357 29.055 28.0203 27.6853L25.3364 24.5802C22.7594 27.043 19.3496 28.3241 15.8203 28.0931C13.882 27.9625 12.001 27.34 10.3629 26.2842C8.72476 25.2284 7.38289 23.7745 6.45903 22.053L3.10265 24.1105C4.30154 26.345 6.04618 28.2396 8.16335 29.6105C10.2805 30.9814 12.7118 31.7852 15.2255 31.9542C17.7392 32.1232 20.2587 31.6515 22.5539 30.5821C24.8491 29.5126 26.8488 27.878 28.3753 25.8277Z"
                  fill="#4285F4"
                />
                <path
                  d="M16 4C17.5759 4 19.1363 4.31038 20.5922 4.91345C22.0481 5.51651 23.371 6.40042 24.4853 7.51472L27.3137 4.68629C25.8134 3.18591 24.005 2.06673 22.0119 1.29285C20.0188 0.518973 17.8872 0.109355 15.7269 0.0838841C13.5666 0.0584128 11.4261 0.417835 9.4169 1.143C7.40769 1.86817 5.56426 2.94498 3.97972 4.31468L6.66358 7.41984C9.24058 4.95696 12.6504 3.6759 16.1797 3.90691C18.118 4.0375 19.999 4.66002 21.6371 5.7158C23.2752 6.77158 24.6171 8.22554 25.541 9.94705L28.8974 7.88951C27.6985 5.655 25.9538 3.76036 23.8367 2.38951C21.7195 1.01867 19.2882 0.214815 16.7745 0.045811C14.2608 -0.123193 11.7413 0.348508 9.44613 1.41793C7.15096 2.48736 5.15121 4.122 3.62473 6.17234Z"
                  fill="#4285F4"
                />
              </svg>
            </div>
            <div className="flex flex-col text-[#555] opacity-80 mt-0.5 leading-[1.1] items-center">
              <span className="text-[8px] font-medium tracking-tighter">protected by</span>
              <span className="text-[11px] font-bold tracking-tight text-[#2b2b2b]">reCAPTCHA</span>
            </div>
            <div className="flex gap-1 text-[7px] text-gray-500 font-sans tracking-tight mt-1">
              <a href="https://policies.google.com/privacy" className="hover:underline">
                Privacy
              </a>
              <span>-</span>
              <a href="https://policies.google.com/terms" className="hover:underline">
                Terms
              </a>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}

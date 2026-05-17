"use client";
import { CopilotPopup } from "@copilotkit/react-ui";
import Image from "next/image";
import Link from "next/link";
import { ThreatRadarWidget } from "../components/a2ui/ThreatRadarWidget";
import CookieConsent from "../components/CookieConsent";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-white font-sans text-gray-900 leading-relaxed">
      {/* AG-UI Component Payload Listener */}
      <ThreatRadarWidget />

      {/* Omniscient Copilot Popup */}
      <CopilotPopup
        defaultOpen={true}
        labels={{
          title: "UphillSnowball 10-Fingers Oracle",
          initial:
            "Target established. Commander, input the target ticker or IP for C++ Fast Monte Carlo & Cloudflare Radar dilution.",
        }}
        className="z-50 shadow-[0_0_20px_rgba(16,185,129,0.3)]"
      />

      {/* Dual Layer Corporate Navbar */}
      <header className="absolute top-0 z-50 w-full">
        {/* Top Utility Bar */}
        <div className="w-full bg-black/80 text-white border-b border-white/10 hidden md:flex justify-end pr-12 h-10 items-center text-[11px] font-bold tracking-widest gap-8">
          <div className="flex gap-4 items-center uppercase">
            <button type="button" className="hover:text-emerald-400 transition-colors">
              A-
            </button>
            <button type="button" className="hover:text-emerald-400 transition-colors">
              A+
            </button>
            <button
              type="button"
              className="hover:text-emerald-400 transition-colors inline-flex items-center gap-1.5"
            >
              <span className="h-3 w-3 rounded-full bg-white/20"></span> Contrast
            </button>
            <Link
              href="/accessibility"
              className="hover:text-emerald-400 transition-colors flex items-center gap-1.5"
            >
              <span className="h-3 w-3 rounded-full border border-current flex items-center justify-center text-[8px]">
                i
              </span>{" "}
              Accessibility
            </Link>
          </div>
          <Link
            href="/contact/contact-sales-inquiries"
            className="border border-white/40 rounded-full px-4 py-1 hover:bg-white hover:text-black transition-all"
          >
            CONTACT SALES
          </Link>
        </div>

        {/* Main Navigation */}
        <div className="w-full bg-transparent flex h-24 items-center justify-between px-8 lg:px-12">
          {/* Brand Logo - 3D Leaf + Text */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative h-14 w-14 flex items-center justify-center overflow-hidden flex-shrink-0 filter drop-shadow-[0_0_10px_rgba(16,185,129,0.5)]">
              <Image
                src="/circuit-leaf-logo.jpg"
                alt="UphillSnowball Leaf"
                fill
                className="object-contain"
              />
            </div>
            <div className="flex flex-col">
              <span className="text-3xl font-black tracking-tighter text-white font-display uppercase group-hover:text-emerald-400 transition-colors drop-shadow-xl">
                UphillSnowball
              </span>
              <span className="text-[10px] font-bold tracking-[0.25em] text-emerald-400 uppercase mt-0.5">
                By ShadowTag Ai
              </span>
            </div>
          </Link>

          {/* Core Routes via Nested Hover Dropdowns */}
          <nav className="hidden lg:flex items-center gap-4 xl:gap-8">
            <div className="relative group">
              <Link
                href="/about-us"
                className="text-sm font-bold text-white uppercase tracking-widest hover:text-emerald-400 transition-colors py-4 inline-block drop-shadow-md"
              >
                About Us
              </Link>
              <div className="absolute top-[100%] left-0 w-56 bg-[#1b103c] border-t-2 border-emerald-500 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <Link
                  href="/about-us/overview"
                  className="block px-4 py-3 text-sm text-gray-300 hover:bg-black/20 hover:text-emerald-400 border-b border-white/10"
                >
                  Overview
                </Link>
                <Link
                  href="/about-us/company-presentation"
                  className="block px-4 py-3 text-sm text-gray-300 hover:bg-black/20 hover:text-emerald-400"
                >
                  Company Presentation
                </Link>
              </div>
            </div>

            <Link
              href="/products"
              className="text-sm font-bold text-white uppercase tracking-widest hover:text-emerald-400 transition-colors py-4 inline-block drop-shadow-md"
            >
              Products
            </Link>

            <div className="relative group">
              <Link
                href="/news-events"
                className="text-sm font-bold text-white uppercase tracking-widest hover:text-emerald-400 transition-colors py-4 inline-block drop-shadow-md"
              >
                Media & Events
              </Link>
              <div className="absolute top-[100%] left-0 w-56 bg-[#1b103c] border-t-2 border-emerald-500 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <Link
                  href="/news-events/press-releases"
                  className="block px-4 py-3 text-sm text-gray-300 hover:bg-black/20 hover:text-emerald-400 border-b border-white/10"
                >
                  Press Releases
                </Link>
                <Link
                  href="/news-events/media-coverage"
                  className="block px-4 py-3 text-sm text-gray-300 hover:bg-black/20 hover:text-emerald-400"
                >
                  Media Coverage
                </Link>
              </div>
            </div>

            <div className="relative group">
              <a
                href="/shadowtag_investor_deck.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-bold text-white uppercase tracking-widest hover:text-emerald-400 transition-colors py-4 inline-block drop-shadow-md flex items-center gap-1.5"
                aria-label="Investors Menu"
              >
                Investors
                <svg
                  className="w-4 h-4 text-white/70 group-hover:text-emerald-400 transition-colors"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </a>
              <div className="absolute top-[100%] left-0 w-64 bg-[#1b103c] border-t-2 border-emerald-500 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <Link
                  href="/corporate-governance"
                  className="block px-4 py-3 text-sm text-gray-300 hover:bg-black/20 hover:text-emerald-400 border-b border-white/10"
                >
                  Corporate Governance
                </Link>
                <Link
                  href="/financials"
                  className="block px-4 py-3 text-sm text-gray-300 hover:bg-black/20 hover:text-emerald-400"
                >
                  Financials
                </Link>
              </div>
            </div>

            <Link
              href="/contact"
              className="text-sm font-bold text-white uppercase tracking-widest hover:text-emerald-400 transition-colors py-4 inline-block drop-shadow-md"
            >
              Contact
            </Link>
            <Link
              href="/careers"
              className="text-sm font-bold text-white uppercase tracking-widest hover:text-emerald-400 transition-colors py-4 inline-block drop-shadow-md"
            >
              Careers
            </Link>
          </nav>
        </div>
      </header>

      {/* Interactive EU Compliance Cookie Banner Component */}
      <CookieConsent />

      {/* Hero Section */}
      <section className="relative flex min-h-[600px] w-full items-center">
        <div className="absolute inset-0 z-0 overflow-hidden perspective-1000">
          <Image
            src="/hero-bg.png"
            alt="Industrial Drones Matrix"
            fill
            priority
            className="object-cover object-center"
          />
          {/* Dark Overlay for text readability, mimicking corporate style */}
          <div className="absolute inset-0 bg-black/50" />

          {/* 3D Volumetric Hologram Overlay (Clipped to Circle) */}
          <div className="absolute top-[20%] right-[10%] w-[300px] h-[300px] md:w-[450px] md:h-[450px] xl:right-[15%] xl:w-[500px] xl:h-[500px] rounded-full overflow-hidden shadow-[0_0_40px_rgba(16,185,129,0.5)] transform-gpu hover:scale-105 transition-transform duration-700">
            {/* The generated 3D square image is clipped perfectly into the inner circle without extra shading */}
            <Image
              src="/leaf_3d.png"
              alt="3D Holographic Globe Leaf"
              fill
              className="object-cover filter mix-blend-screen opacity-95"
            />
          </div>
        </div>

        <div className="relative z-10 w-full max-w-7xl mx-auto px-6 lg:px-8 pt-20 pb-32">
          <div className="max-w-3xl bg-white/5 backdrop-blur-md p-10 border-l-4 border-emerald-500 shadow-2xl rounded-sm mb-8 relative">
            <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-white mb-6 uppercase leading-tight font-display drop-shadow-2xl">
              FOR WHEN YOU ARE
              <br />
              NOT THERE
            </h1>
            <p className="text-xl text-gray-100 max-w-xl font-light drop-shadow-lg leading-relaxed">
              UphillSnowball by ShadowTagAi provides industry-spanning recursive self-improvement,
              research, and monitoring loops. Hallucination-free and impervious to rogue agents. We
              provide research to finance, law, medicine, academia, defense, and even the home
              consumer.
            </p>
          </div>

          <div className="max-w-3xl bg-white/5 backdrop-blur-md p-6 border-l-4 border-emerald-500 shadow-2xl rounded-sm">
            <p className="text-lg text-emerald-100 font-light drop-shadow-lg leading-relaxed italic">
              While at enterprise levels, protecting our fellow AI providers against violations of
              EU &apos;26 and California Minor AI laws.
            </p>
          </div>
        </div>
      </section>

      {/* Corporate Compliance Banner */}
      <section className="py-20 bg-zinc-900 text-white border-y border-zinc-800 w-full overflow-hidden relative">
        <div className="absolute inset-0 opacity-5 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]"></div>
        <div className="max-w-4xl mx-auto px-6 lg:px-8 text-center relative z-10">
          <h2 className="text-3xl font-bold mb-6 font-display text-white tracking-wide">
            Like A Snowball Gaining Momentum While It Rolls Uphill
          </h2>
          <p className="text-2xl text-emerald-400 mb-6 font-display leading-relaxed">
            ShadowTagAi&apos;s UphillSnowball Defies The Physics Of Your Business.
          </p>
          <p className="text-lg text-zinc-300 font-light leading-relaxed">
            Engineered to loop recursively through your research providing verified, citable
            internal and external sources, with an audit trail. Potentially indefinitely, with a
            human on the loop. Included in the premium packages, preemptive avoidance of sanction
            for the entire network, under both California AI Minor Law and the pending EU &apos;26
            AI laws. ShadowTagAi&apos;s premium safety gates ensure uncompromising deployment safety
            globally.
          </p>
        </div>
      </section>

      {/* Corporate Three-Column Grid */}
      <section className="py-24 bg-white text-gray-900 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-16">
            {/* Column 1: Recent News */}
            <div>
              <h3 className="text-2xl font-bold mb-8 font-display uppercase border-b border-gray-200 pb-3 tracking-wide">
                Recent News
              </h3>
              <ul className="space-y-6">
                <li className="group">
                  <p className="text-xs font-bold text-gray-400 mb-2 uppercase tracking-widest">
                    January 27, 2026
                  </p>
                  <Link
                    href="/"
                    className="text-lg font-medium leading-tight group-hover:text-emerald-700 transition-colors block"
                  >
                    ShadowTagAi Incorporated
                  </Link>
                </li>
              </ul>
              <Link
                href="/"
                className="inline-block mt-8 text-sm font-bold text-emerald-700 uppercase tracking-widest hover:text-gray-900 transition-colors border-b-2 border-emerald-500 pb-1"
              >
                All News &rarr;
              </Link>
            </div>

            {/* Column 2: Quick Links */}
            <div>
              <h3 className="text-2xl font-bold mb-8 font-display uppercase border-b border-gray-200 pb-3 tracking-wide">
                Quick Links
              </h3>
              <ul className="space-y-4">
                <li>
                  <Link
                    href="/"
                    className="text-base font-medium text-gray-700 hover:text-emerald-700 border-b border-gray-100 pb-3 block flex justify-between items-center group transition-colors"
                  >
                    Corporate Governance{" "}
                    <span className="text-gray-300 group-hover:text-emerald-700 transition-colors">
                      &rarr;
                    </span>
                  </Link>
                </li>
                <li>
                  <Link
                    href="/"
                    className="text-base font-medium text-gray-700 hover:text-emerald-700 border-b border-gray-100 pb-3 block flex justify-between items-center group transition-colors"
                  >
                    Investor Presentation{" "}
                    <span className="text-gray-300 group-hover:text-emerald-700 transition-colors">
                      &rarr;
                    </span>
                  </Link>
                </li>
              </ul>
            </div>

            {/* Column 3: Upcoming Events */}
            <div>
              <h3 className="text-2xl font-bold mb-8 font-display uppercase border-b border-gray-200 pb-3 tracking-wide">
                Upcoming Events
              </h3>
              <div className="bg-gray-50 p-8 border border-gray-200 rounded-sm">
                <p className="text-sm font-medium text-gray-500 italic text-center">
                  There are currently no upcoming events scheduled at this time. Please check back
                  later for updates.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Corporate Footer */}
      <footer className="bg-gray-50 py-16 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
            <div className="col-span-1 md:col-span-2 pr-8">
              <div className="flex items-center gap-3 mb-6">
                {/* Footer Corporate Logo */}
                <div className="relative h-10 w-10 rounded bg-black flex items-center justify-center overflow-hidden flex-shrink-0">
                  <Image
                    src="/logo.png"
                    alt="ShadowTag Corporate Logo"
                    fill
                    className="object-cover"
                  />
                </div>
                <span className="text-xl font-bold tracking-tight text-gray-900 font-display">
                  SHADOWTAG AI
                </span>
              </div>
              <p className="text-gray-500 text-sm leading-relaxed max-w-sm">
                Empowering the future of localized sovereign compute and global AI protocol
                enforcement. Based in California, protecting globally.
              </p>
            </div>

            <div className="col-span-1 md:col-span-2">
              <h4 className="text-sm font-bold text-gray-900 mb-6 font-display uppercase tracking-widest">
                Contact Information
              </h4>
              <address className="not-italic space-y-1 text-sm font-medium text-gray-600">
                <p className="font-extrabold text-gray-900 tracking-wide">Erik L. Hancock</p>
                <p className="text-emerald-700 font-bold tracking-widest uppercase mb-4 text-xs pb-3 border-b border-gray-200 inline-block">
                  Founder — CEO
                </p>

                <p className="font-bold text-gray-900 pt-1">ShadowTagAi Inc.</p>
                <div className="border-l-2 border-emerald-500 pl-3 my-2 space-y-0.5">
                  <p>495 N Main St., #119</p>
                  <p>Lakeport, CA 95453</p>
                </div>

                <p className="mt-4">
                  <span className="text-gray-900 font-bold w-20 inline-block">Telephone:</span>{" "}
                  <a href="tel:369-235-5643" className="hover:text-emerald-700 transition-colors">
                    (369) 235-5643
                  </a>
                </p>
                <p>
                  <span className="text-gray-900 font-bold w-20 inline-block">Facsimile:</span>{" "}
                  <span>(707) 263-8659</span>
                </p>
                <p>
                  <span className="text-gray-900 font-bold w-20 inline-block">Email:</span>{" "}
                  <a
                    href="mailto:redacted@shadowtag-v4.local"
                    className="hover:text-emerald-700 transition-colors"
                  >
                    redacted@shadowtag-v4.local
                  </a>
                </p>
              </address>
            </div>
          </div>

          <div className="pt-8 border-t border-gray-200 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-xs text-gray-400 font-medium">
              &copy; {new Date().getFullYear()} ShadowTagAI, Inc. All rights reserved.
            </p>
            <div className="flex space-x-6 text-xs font-medium text-gray-400">
              <Link href="/" className="hover:text-gray-900 transition-colors">
                Privacy Policy
              </Link>
              <Link href="/" className="hover:text-gray-900 transition-colors">
                Terms of Service
              </Link>
              <Link href="/" className="hover:text-gray-900 transition-colors">
                Disclaimer
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

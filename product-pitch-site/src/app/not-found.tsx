import Link from "next/link";

/**
 * Item 17: Branded 404 page with KovelAI design system.
 * Uses the same dark glass aesthetic as the rest of the site.
 */
export default function NotFound() {
  return (
    <main className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
      <div className="text-center px-6 max-w-lg">
        {/* Animated 404 number */}
        <div className="relative mb-8">
          <h1
            className="text-[10rem] md:text-[14rem] font-black leading-none select-none"
            style={{
              background: "linear-gradient(135deg, #00bcd4, #7c4dff, #ff6b35)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              opacity: 0.15,
            }}
          >
            404
          </h1>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#00bcd4] to-[#00e5ff] flex items-center justify-center text-3xl font-bold text-[#0a0a0f] shadow-lg shadow-[#00bcd4]/20 animate-pulse">
              K
            </div>
          </div>
        </div>

        <h2 className="text-2xl md:text-3xl font-bold mb-4">
          Page <span className="gradient-text">Not Found</span>
        </h2>

        <p className="text-[#8b949e] mb-8 leading-relaxed">
          This page doesn&apos;t exist or has been moved. Let&apos;s get you back to building
          privileged legal AI.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/" className="cta-button text-sm">
            ← Back to Home
          </Link>
          <Link href="/#pricing" className="cta-button-outline text-sm">
            View Pricing
          </Link>
        </div>

        {/* Decorative gradient orb */}
        <div
          className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full pointer-events-none"
          style={{
            background: "radial-gradient(circle, rgba(0,188,212,0.06) 0%, transparent 70%)",
          }}
        />
      </div>
    </main>
  );
}

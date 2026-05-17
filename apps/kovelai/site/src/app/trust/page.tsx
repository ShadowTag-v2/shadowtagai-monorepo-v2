"use client";
import { motion } from "framer-motion";

export default function TrustManifestoPage() {
  return (
    <main className="min-h-screen pt-32 pb-24 px-8 max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="text-center mb-16"
      >
        <span className="section-label">Trust & Security Manifesto</span>
        <h1 className="section-title text-[clamp(2.5rem,5vw,4rem)] mb-6">
          The <span style={{ color: "var(--color-gold)" }}>Privilege-Preserving</span> Architecture
        </h1>
        <p className="section-desc mx-auto text-lg max-w-3xl">
          At KovelAI, we believe that AI should empower legal practitioners without ever
          compromising the sanctity of the attorney-client seal. Our architecture is built from the
          ground up to guarantee data isolation, sovereign control, and cryptographically verifiable
          security.
        </p>
      </motion.div>

      {/* Bento Box Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 auto-rows-[280px]">
        {/* Bento Box 1 - Zero Retention */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="glass-card md:col-span-2 lg:col-span-2 flex flex-col justify-between relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-64 h-64 bg-gold/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
          <div className="relative z-10">
            <div className="w-12 h-12 rounded-full bg-surface-highest flex items-center justify-center mb-4 text-gold">
              <svg
                aria-hidden="true"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                <path d="M9 12l2 2 4-4" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-foreground mb-3">Zero Data Retention</h3>
            <p className="text-secondary-text">
              We do not train our models on your case files, nor do we persist your queries longer
              than the execution context. Your intellectual property remains strictly yours.
            </p>
          </div>
        </motion.div>

        {/* Bento Box 2 - SOC2 */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="glass-card md:col-span-1 lg:col-span-2 flex flex-col justify-center items-center text-center bg-gradient-to-br from-surface-highest to-surface"
        >
          <h3 className="text-5xl font-black text-gold mb-2">SOC 2</h3>
          <p className="text-sm font-medium text-outline uppercase tracking-widest">
            Type II Certified
          </p>
        </motion.div>

        {/* Bento Box 3 - End-to-End Encryption */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="glass-card md:col-span-1 lg:col-span-1 flex flex-col justify-between"
        >
          <div>
            <div className="w-10 h-10 rounded bg-blue-container/10 flex items-center justify-center mb-4 text-blue">
              <svg
                aria-hidden="true"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                <path d="M7 11V7a5 5 0 0110 0v4" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-foreground mb-2">E2E Encryption</h3>
            <p className="text-sm text-secondary-text">
              AES-256 encryption at rest and TLS 1.3 in transit. Keys are managed via GCP KMS with
              BYOK support.
            </p>
          </div>
        </motion.div>

        {/* Bento Box 4 - Epistemic Airgap */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="glass-card md:col-span-2 lg:col-span-3 flex flex-col justify-between relative overflow-hidden group"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-surface to-transparent z-0" />
          <div className="relative z-10 w-full md:w-2/3">
            <span className="inline-block px-3 py-1 text-xs font-bold uppercase tracking-wider text-error bg-error/10 border border-error/20 rounded mb-4">
              Proprietary Protocol
            </span>
            <h3 className="text-2xl font-bold text-foreground mb-3">Epistemic Airgap Doctrine</h3>
            <p className="text-secondary-text">
              Our unique architecture physically separates deterministic logic boundaries from
              probabilistic reasoning boundaries. This structural isolation guarantees that LLMs can
              never unilaterally execute destructive queries against your legal databases.
            </p>
          </div>
        </motion.div>

        {/* Bento Box 5 - Immutable Audit */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="glass-card md:col-span-3 lg:col-span-4 flex items-center justify-between overflow-hidden relative border-gold/30"
        >
          <div className="absolute right-0 top-0 h-full w-1/2 bg-[radial-gradient(ellipse_at_right,_var(--tw-gradient-stops))] from-gold/10 via-surface/5 to-transparent pointer-events-none" />
          <div className="relative z-10 flex flex-col md:flex-row gap-8 items-center w-full">
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-foreground mb-3">Immutable Audit Ledger</h3>
              <p className="text-secondary-text max-w-xl">
                Every AI interaction, context retrieval, and decision path is cryptographically
                hashed and logged to an append-only ledger. When a court demands provenance for an
                AI-assisted argument, you have the exact chain of custody instantly available.
              </p>
            </div>
            <div className="shrink-0">
              <button type="button" className="btn-gold shadow-ambient">
                Download Security Whitepaper
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}

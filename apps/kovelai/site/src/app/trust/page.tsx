'use client';

import { motion, useInView } from 'framer-motion';
import { useRef, useCallback, useState } from 'react';
import Nav from '@/components/shared/Nav';
import Footer from '@/components/shared/Footer';
import ContactModal from '@/components/shared/ContactModal';

/* ─── Animated Section Wrapper ─── */
function AnimatedSection({
  children,
  className = '',
  delay = 0,
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 32 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 32 }}
      transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ─── Shield Icon SVG ─── */
function ShieldIcon({ className = '' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      className={className}
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"
      />
    </svg>
  );
}

/* ─── Security Badge Data ─── */
const CERTIFICATIONS = [
  {
    id: 'soc2',
    title: 'SOC 2 Type II',
    description: 'Annual audit by independent CPA firm covering security, availability, and confidentiality trust service criteria.',
    icon: '🛡️',
    status: 'Certified',
  },
  {
    id: 'hipaa',
    title: 'HIPAA Compliant',
    description: 'BAA-ready infrastructure with PHI safeguards for firms handling healthcare litigation data.',
    icon: '🏥',
    status: 'Compliant',
  },
  {
    id: 'gdpr',
    title: 'GDPR Article 28',
    description: 'Data Processing Agreements and EU data residency options for international law firms.',
    icon: '🇪🇺',
    status: 'Compliant',
  },
  {
    id: 'aba',
    title: 'ABA Model Rule 1.6',
    description: 'Architecture designed to preserve attorney-client privilege during AI-assisted legal operations.',
    icon: '⚖️',
    status: 'By Design',
  },
];

const SECURITY_PILLARS = [
  {
    id: 'encryption',
    title: 'Encryption at Rest & Transit',
    description: 'AES-256 encryption for data at rest. TLS 1.3 for all data in transit. Customer-managed encryption keys (CMEK) available for Enterprise.',
    gradient: 'from-[#aac7ff]/20 to-[#3e90ff]/10',
  },
  {
    id: 'privilege',
    title: 'Privilege Preservation',
    description: 'Zero-knowledge architecture ensures attorney-client privilege is never compromised. LLM routing isolates each matter with Heppner-compliant guardrails.',
    gradient: 'from-[#e6c487]/20 to-[#c9a96e]/10',
  },
  {
    id: 'audit',
    title: 'Immutable Audit Trails',
    description: 'Every AI interaction, document access, and system event is cryptographically logged with tamper-evident checksums for regulatory review.',
    gradient: 'from-[#b8c8f2]/20 to-[#aac7ff]/10',
  },
  {
    id: 'isolation',
    title: 'Tenant Isolation',
    description: 'Firm data is logically and cryptographically isolated. No cross-tenant data leakage. Dedicated compute pools for Enterprise tier.',
    gradient: 'from-[#e6c487]/20 to-[#aac7ff]/10',
  },
  {
    id: 'residency',
    title: 'Data Residency',
    description: 'Choose where your data lives. US, EU, and APAC regions available. Data never leaves your selected jurisdiction without explicit consent.',
    gradient: 'from-[#3e90ff]/20 to-[#b8c8f2]/10',
  },
  {
    id: 'access',
    title: 'Zero-Trust Access',
    description: 'RBAC with MFA enforcement. SSO via SAML 2.0 and OIDC. Session tokens rotate every 15 minutes. Principle of least privilege throughout.',
    gradient: 'from-[#c9a96e]/20 to-[#e6c487]/10',
  },
];

const INFRASTRUCTURE = [
  { label: 'Cloud Provider', value: 'Google Cloud Platform' },
  { label: 'Compute', value: 'Cloud Run (serverless)' },
  { label: 'Database', value: 'Firestore + Cloud SQL' },
  { label: 'CDN', value: 'Cloud Armor + Firebase Hosting' },
  { label: 'WAF', value: '4 Cloud Armor rules active' },
  { label: 'Monitoring', value: 'Cloud Monitoring + 8 alert policies' },
  { label: 'CI/CD', value: 'Cloud Build with signed artifacts' },
  { label: 'Secret Management', value: 'GCP Secret Manager (FIPS 140-2)' },
];

export default function TrustPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const openModal = useCallback(() => setModalOpen(true), []);
  const closeModal = useCallback(() => setModalOpen(false), []);

  return (
    <>
      <a href="#main-content" className="skip-nav">
        Skip to main content
      </a>
      <Nav onOpenModal={openModal} />

      <main id="main-content" className="pt-24 pb-16">
        {/* ─── Hero Section ─── */}
        <section className="relative overflow-hidden py-20">
          {/* Aura Blobs */}
          <div
            className="absolute top-[-120px] left-[-80px] w-[500px] h-[500px] rounded-full opacity-30 blur-[120px] pointer-events-none"
            style={{
              background: 'radial-gradient(circle, rgba(170,199,255,0.4), transparent 70%)',
              animation: 'aura-drift 12s ease-in-out infinite',
            }}
            aria-hidden="true"
          />
          <div
            className="absolute bottom-[-80px] right-[-60px] w-[400px] h-[400px] rounded-full opacity-20 blur-[100px] pointer-events-none"
            style={{
              background: 'radial-gradient(circle, rgba(230,196,135,0.3), transparent 70%)',
              animation: 'aura-drift-reverse 15s ease-in-out infinite',
            }}
            aria-hidden="true"
          />

          <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <AnimatedSection>
              <div className="text-center max-w-3xl mx-auto">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-8">
                  <ShieldIcon className="w-5 h-5 text-[#e6c487]" />
                  <span className="text-sm font-medium text-[#d0c5b5]">
                    Security Manifesto
                  </span>
                </div>
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-[#d7e3fc] mb-6">
                  Built for the{' '}
                  <span className="bg-gradient-to-r from-[#e6c487] to-[#c9a96e] bg-clip-text text-transparent">
                    Standard of Care
                  </span>
                </h1>
                <p className="text-lg sm:text-xl text-[#d0c5b5] leading-relaxed max-w-2xl mx-auto">
                  KovelAI&apos;s security architecture is designed from first principles
                  to preserve attorney-client privilege while enabling AI-powered
                  legal operations at scale.
                </p>
              </div>
            </AnimatedSection>
          </div>
        </section>

        {/* ─── Certifications Grid ─── */}
        <section className="py-16" aria-labelledby="certifications-heading">
          <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
            <AnimatedSection>
              <h2
                id="certifications-heading"
                className="text-2xl sm:text-3xl font-bold text-[#d7e3fc] text-center mb-12"
              >
                Compliance & Certifications
              </h2>
            </AnimatedSection>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {CERTIFICATIONS.map((cert, i) => (
                <AnimatedSection key={cert.id} delay={i * 0.1}>
                  <div className="glass-card h-full flex flex-col items-center text-center">
                    <span className="text-4xl mb-4" role="img" aria-label={cert.title}>
                      {cert.icon}
                    </span>
                    <h3 className="text-lg font-semibold text-[#d7e3fc] mb-2">
                      {cert.title}
                    </h3>
                    <p className="text-sm text-[#d0c5b5] mb-4 flex-1">
                      {cert.description}
                    </p>
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-[#e6c487]/10 text-[#e6c487] border border-[#e6c487]/20">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#e6c487]" />
                      {cert.status}
                    </span>
                  </div>
                </AnimatedSection>
              ))}
            </div>
          </div>
        </section>

        {/* ─── Security Pillars Bento Grid ─── */}
        <section className="py-16" aria-labelledby="security-heading">
          <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
            <AnimatedSection>
              <h2
                id="security-heading"
                className="text-2xl sm:text-3xl font-bold text-[#d7e3fc] text-center mb-4"
              >
                Security Architecture
              </h2>
              <p className="text-[#d0c5b5] text-center max-w-2xl mx-auto mb-12">
                Six pillars of defense-in-depth protecting your firm&apos;s most
                sensitive data.
              </p>
            </AnimatedSection>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {SECURITY_PILLARS.map((pillar, i) => (
                <AnimatedSection key={pillar.id} delay={i * 0.08}>
                  <div
                    className={`glass-card h-full relative overflow-hidden group`}
                  >
                    {/* Gradient accent */}
                    <div
                      className={`absolute inset-0 bg-gradient-to-br ${pillar.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
                      aria-hidden="true"
                    />
                    <div className="relative z-10">
                      <div className="w-10 h-10 rounded-lg bg-[#e6c487]/10 flex items-center justify-center mb-4">
                        <ShieldIcon className="w-5 h-5 text-[#e6c487]" />
                      </div>
                      <h3 className="text-lg font-semibold text-[#d7e3fc] mb-3">
                        {pillar.title}
                      </h3>
                      <p className="text-sm text-[#d0c5b5] leading-relaxed">
                        {pillar.description}
                      </p>
                    </div>
                  </div>
                </AnimatedSection>
              ))}
            </div>
          </div>
        </section>

        {/* ─── Heppner Compliance Banner ─── */}
        <section className="py-16" aria-labelledby="heppner-heading">
          <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
            <AnimatedSection>
              <div className="glass-card relative overflow-hidden">
                <div
                  className="absolute inset-0 bg-gradient-to-r from-[#e6c487]/5 to-[#aac7ff]/5"
                  aria-hidden="true"
                />
                <div className="relative z-10 flex flex-col lg:flex-row items-center gap-8 p-4 sm:p-8">
                  <div className="flex-shrink-0">
                    <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#e6c487]/20 to-[#c9a96e]/10 flex items-center justify-center">
                      <span className="text-4xl" role="img" aria-label="Scales of justice">
                        ⚖️
                      </span>
                    </div>
                  </div>
                  <div className="flex-1 text-center lg:text-left">
                    <h2
                      id="heppner-heading"
                      className="text-xl sm:text-2xl font-bold text-[#d7e3fc] mb-3"
                    >
                      Heppner-Compliant by Architecture
                    </h2>
                    <p className="text-[#d0c5b5] leading-relaxed max-w-2xl">
                      Following the{' '}
                      <em className="text-[#aac7ff]">
                        Heppner v. Agentic Systems, Inc.
                      </em>{' '}
                      (S.D.N.Y. 2026) ruling, KovelAI implements mandatory
                      privilege-preservation guardrails at the infrastructure level.
                      Our zero-knowledge LLM routing ensures no model retains, trains on,
                      or indexes privileged communications — verified by independent audit.
                    </p>
                  </div>
                </div>
              </div>
            </AnimatedSection>
          </div>
        </section>

        {/* ─── Infrastructure Table ─── */}
        <section className="py-16" aria-labelledby="infrastructure-heading">
          <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
            <AnimatedSection>
              <h2
                id="infrastructure-heading"
                className="text-2xl sm:text-3xl font-bold text-[#d7e3fc] text-center mb-12"
              >
                Infrastructure Stack
              </h2>
            </AnimatedSection>

            <AnimatedSection delay={0.1}>
              <div className="glass-card overflow-hidden">
                <table className="w-full" role="table">
                  <caption className="sr-only">
                    KovelAI infrastructure components
                  </caption>
                  <thead>
                    <tr className="border-b border-[#4d463a]/20">
                      <th
                        scope="col"
                        className="text-left py-3 px-4 sm:px-6 text-sm font-semibold text-[#e6c487]"
                      >
                        Component
                      </th>
                      <th
                        scope="col"
                        className="text-left py-3 px-4 sm:px-6 text-sm font-semibold text-[#e6c487]"
                      >
                        Technology
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {INFRASTRUCTURE.map((item, i) => (
                      <tr
                        key={item.label}
                        className={
                          i < INFRASTRUCTURE.length - 1
                            ? 'border-b border-[#4d463a]/10'
                            : ''
                        }
                      >
                        <td className="py-3 px-4 sm:px-6 text-sm text-[#d0c5b5]">
                          {item.label}
                        </td>
                        <td className="py-3 px-4 sm:px-6 text-sm text-[#d7e3fc] font-medium">
                          {item.value}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </AnimatedSection>
          </div>
        </section>

        {/* ─── CTA Section ─── */}
        <section className="py-20" aria-labelledby="trust-cta-heading">
          <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
            <AnimatedSection>
              <div className="text-center max-w-2xl mx-auto">
                <h2
                  id="trust-cta-heading"
                  className="text-2xl sm:text-3xl font-bold text-[#d7e3fc] mb-4"
                >
                  Ready to see our security in action?
                </h2>
                <p className="text-[#d0c5b5] mb-8">
                  Schedule a security deep-dive with our team. We&apos;ll walk through
                  our architecture, provide audit documentation, and answer every question.
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                  <button
                    type="button"
                    onClick={openModal}
                    className="btn-gold text-base py-3 px-8"
                  >
                    Request Security Review
                  </button>
                  <a
                    href="/"
                    className="btn-ghost text-base py-3 px-8"
                  >
                    Back to Home
                  </a>
                </div>
              </div>
            </AnimatedSection>
          </div>
        </section>
      </main>

      <Footer onOpenModal={openModal} />
      <ContactModal isOpen={modalOpen} onClose={closeModal} />
    </>
  );
}

'use client';

import { motion, useInView } from 'framer-motion';
import { useCallback, useRef, useState } from 'react';
import ContactModal from '@/components/shared/ContactModal';
import Footer from '@/components/shared/Footer';
import Nav from '@/components/shared/Nav';

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

const SECTIONS = [
  {
    id: 'collection',
    title: '1. Information We Collect',
    content: `KovelAI collects the minimum information necessary to provide our services:

• **Account Information:** Firm name, administrator email, and billing details provided during registration.
• **Session Metadata:** Timestamp, duration, and token count for billing and compliance audit purposes. Session content is never stored.
• **Usage Analytics:** Aggregated, anonymized platform usage metrics via Google Analytics 4 with IP anonymization enabled.

**What We Do NOT Collect:**
• Client search queries or AI conversation content
• Browser history or browsing behavior
• Documents, files, or case materials
• Any personally identifiable information (PII) of your clients`,
  },
  {
    id: 'retention',
    title: '2. Zero-Retention Architecture',
    content: `KovelAI operates a zero-retention architecture for all privileged session data:

• All AI inference occurs in ephemeral compute instances that are cryptographically shredded upon session termination.
• No client queries, responses, or session content is written to persistent storage at any point.
• Session metadata (timestamps, token counts) is retained for 90 days for billing reconciliation, then permanently deleted.
• Infrastructure logs are retained for 30 days for security monitoring, contain no session content, and are automatically purged.`,
  },
  {
    id: 'sharing',
    title: '3. Information Sharing',
    content: `KovelAI does not sell, rent, or trade your information. We share data only in these limited circumstances:

• **Service Providers:** Google Cloud Platform (infrastructure), Stripe (payment processing). All providers are bound by data processing agreements.
• **Legal Compliance:** We may disclose information if required by law, subpoena, or court order — however, our zero-retention architecture means we physically cannot produce session content that was never stored.
• **Business Transfer:** In the event of a merger or acquisition, your data would be subject to the same privacy protections.`,
  },
  {
    id: 'security',
    title: '4. Security Measures',
    content: `• AES-256 encryption at rest for all persistent data
• TLS 1.3 for all data in transit
• SOC 2 Type II certified infrastructure
• RBAC with MFA enforcement for all administrator accounts
• 15-minute session token rotation
• Cloud Armor WAF with 4 active security rules
• Immutable audit trails with tamper-evident checksums
• Penetration testing conducted annually by independent security firms`,
  },
  {
    id: 'rights',
    title: '5. Your Rights',
    content: `Depending on your jurisdiction, you may have the following rights:

• **Access:** Request a copy of the personal data we hold about you.
• **Correction:** Request correction of inaccurate personal data.
• **Deletion:** Request deletion of your personal data (subject to legal retention obligations).
• **Portability:** Request your data in a structured, machine-readable format.
• **Objection:** Object to processing of your personal data for specific purposes.

**GDPR (EU/EEA):** We process data under legitimate interest (Article 6(1)(f)) and contractual necessity (Article 6(1)(b)). DPA available upon request.
**CCPA (California):** We do not sell personal information. California residents may exercise their rights by contacting privacy@kovelai.com.`,
  },
  {
    id: 'contact',
    title: '6. Contact & Updates',
    content: `For privacy inquiries, data subject requests, or to report a concern:

• **Email:** privacy@kovelai.com
• **Mail:** ShadowTag AI, Inc. — Privacy Team

This policy is effective as of January 1, 2026 and was last updated on May 4, 2026. We will notify registered users of material changes via email at least 30 days before they take effect.`,
  },
];

export default function PrivacyPage() {
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
        <section className="py-16">
          <div className="max-w-[800px] mx-auto px-4 sm:px-6 lg:px-8">
            <AnimatedSection>
              <div className="text-center mb-16">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-8">
                  <span className="text-sm font-medium text-[#d0c5b5]">🔒 Privacy Policy</span>
                </div>
                <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-[#d7e3fc] mb-6">
                  Your Privacy,{' '}
                  <span className="bg-gradient-to-r from-[#e6c487] to-[#c9a96e] bg-clip-text text-transparent">
                    By Design
                  </span>
                </h1>
                <p className="text-lg text-[#d0c5b5] leading-relaxed max-w-2xl mx-auto">
                  KovelAI&apos;s zero-retention architecture means your clients&apos; privileged
                  data is never stored, never indexed, and never accessible — even to us.
                </p>
              </div>
            </AnimatedSection>

            {SECTIONS.map((section, i) => (
              <AnimatedSection key={section.id} delay={i * 0.05} className="mb-12">
                <div className="glass-card">
                  <h2 className="text-xl font-semibold text-[#d7e3fc] mb-4">{section.title}</h2>
                  <div className="text-sm text-[#d0c5b5] leading-relaxed whitespace-pre-line">
                    {section.content}
                  </div>
                </div>
              </AnimatedSection>
            ))}

            <AnimatedSection delay={0.3}>
              <div className="text-center mt-16">
                <a href="/" className="btn-ghost text-base py-3 px-8">
                  ← Back to Home
                </a>
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

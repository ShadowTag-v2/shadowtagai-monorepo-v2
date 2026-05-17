"use client";

import { motion, useInView } from "framer-motion";
import { useCallback, useRef, useState } from "react";
import ContactModal from "@/components/shared/ContactModal";
import Footer from "@/components/shared/Footer";
import Nav from "@/components/shared/Nav";

function AnimatedSection({
  children,
  className = "",
  delay = 0,
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

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
    id: "acceptance",
    title: "1. Acceptance of Terms",
    content: `By accessing or using KovelAI ("Service"), you agree to be bound by these Terms of Service ("Terms"). If you are using the Service on behalf of a law firm or organization, you represent that you have the authority to bind that entity to these Terms.

If you do not agree to these Terms, you must not access or use the Service.`,
  },
  {
    id: "service",
    title: "2. Description of Service",
    content: `KovelAI provides privilege-preserving AI and web search infrastructure for law firms. The Service includes:

• Privileged client AI chat and web search routing under the Kovel Doctrine framework
• After-hours automated client intake
• Session billing and revenue analytics
• Compliance reporting and audit trail generation

The Service is designed to assist law firms in maintaining attorney-client privilege for client digital activity following In re Heppner (S.D.N.Y. 2026). KovelAI does not provide legal advice and is not a substitute for professional legal judgment.`,
  },
  {
    id: "accounts",
    title: "3. Accounts & Access",
    content: `• You must provide accurate, complete information when creating an account.
• You are responsible for maintaining the security of your account credentials.
• You must immediately notify us of any unauthorized access to your account.
• Each firm administrator account requires multi-factor authentication (MFA).
• You may not share account credentials or allow multiple individuals to use a single account.
• We reserve the right to suspend accounts that violate these Terms.`,
  },
  {
    id: "billing",
    title: "4. Billing & Payment",
    content: `• **Trial Tier:** 10,000 tokens per month at no cost. No credit card required.
• **Professional Tier:** $149/month (or $1,428/year). Billed in advance via Stripe.
• **Enterprise Tier:** Custom pricing. Contact sales for a quote.
• **Beta Discount:** Eligible firms may receive 50% off Professional tier for 3 months using coupon code 3wseBY7Z.
• All fees are non-refundable except as required by applicable law.
• We may change pricing with 30 days' written notice to your billing email.
• Overdue payments may result in service suspension after a 7-day grace period.`,
  },
  {
    id: "privilege",
    title: "5. Privilege & Compliance",
    content: `KovelAI is designed to operate as a Kovel agent under the direction of subscribing law firms. However:

• **No Guarantee of Privilege:** Whether attorney-client privilege applies to any specific communication depends on the facts and applicable law. KovelAI provides infrastructure designed to support privilege claims but does not guarantee that any court will recognize privilege in a given matter.
• **Firm Responsibility:** The subscribing firm is responsible for ensuring that its use of KovelAI complies with applicable ethical rules, including ABA Model Rule 1.6 and state equivalents.
• **Engagement Letters:** Firms are responsible for maintaining appropriate engagement letters with clients that cover the use of AI tools under the firm's direction.`,
  },
  {
    id: "data",
    title: "6. Data & Privacy",
    content: `Your use of the Service is also governed by our Privacy Policy. Key provisions:

• KovelAI uses zero-retention architecture — no client queries, responses, or session content is stored.
• Session metadata is retained for 90 days for billing purposes only.
• We do not use your data to train AI models.
• See our Privacy Policy for full details on data handling practices.`,
  },
  {
    id: "ip",
    title: "7. Intellectual Property",
    content: `• KovelAI, its logos, designs, and documentation are the property of ShadowTagAI, Inc.
• You retain all rights to your firm's data and client information.
• You grant us a limited license to process your data solely for the purpose of providing the Service.
• You may not reverse-engineer, decompile, or attempt to extract the source code of the Service.`,
  },
  {
    id: "liability",
    title: "8. Limitation of Liability",
    content: `TO THE MAXIMUM EXTENT PERMITTED BY LAW:

• THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED.
• KOVELAI SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES.
• OUR TOTAL LIABILITY SHALL NOT EXCEED THE AMOUNT YOU PAID FOR THE SERVICE IN THE 12 MONTHS PRECEDING THE CLAIM.
• WE DO NOT WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED, ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED.`,
  },
  {
    id: "termination",
    title: "9. Termination",
    content: `• You may cancel your subscription at any time through the Stripe customer portal.
• We may suspend or terminate your access for violation of these Terms with 7 days' written notice.
• Upon termination, your right to use the Service ceases immediately.
• Provisions regarding limitation of liability, intellectual property, and dispute resolution survive termination.`,
  },
  {
    id: "governing",
    title: "10. Governing Law & Disputes",
    content: `• These Terms are governed by the laws of the State of New York.
• Any disputes shall be resolved through binding arbitration under JAMS rules in New York, NY.
• You waive any right to participate in a class action lawsuit or class-wide arbitration.
• Notwithstanding the foregoing, either party may seek injunctive relief in any court of competent jurisdiction.`,
  },
  {
    id: "changes",
    title: "11. Changes to Terms",
    content: `We may update these Terms from time to time. We will notify registered users of material changes via email at least 30 days before they take effect. Continued use of the Service after changes take effect constitutes acceptance of the revised Terms.

These Terms are effective as of January 1, 2026 and were last updated on May 4, 2026.

For questions about these Terms, contact legal@kovelai.com.`,
  },
];

export default function TermsPage() {
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
                  <span className="text-sm font-medium text-[#d0c5b5]">📋 Terms of Service</span>
                </div>
                <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-[#d7e3fc] mb-6">
                  Terms of{" "}
                  <span className="bg-gradient-to-r from-[#e6c487] to-[#c9a96e] bg-clip-text text-transparent">
                    Service
                  </span>
                </h1>
                <p className="text-lg text-[#d0c5b5] leading-relaxed max-w-2xl mx-auto">
                  Clear, fair terms designed for legal professionals who expect precision in every
                  agreement — including ours.
                </p>
              </div>
            </AnimatedSection>

            {SECTIONS.map((section, i) => (
              <AnimatedSection key={section.id} delay={i * 0.04} className="mb-10">
                <div className="glass-card">
                  <h2 className="text-xl font-semibold text-[#d7e3fc] mb-4">{section.title}</h2>
                  <div className="text-sm text-[#d0c5b5] leading-relaxed whitespace-pre-line">
                    {section.content}
                  </div>
                </div>
              </AnimatedSection>
            ))}

            <AnimatedSection delay={0.4}>
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

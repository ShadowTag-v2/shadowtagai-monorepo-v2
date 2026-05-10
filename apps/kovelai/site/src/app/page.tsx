'use client';

import { useCallback, useState } from 'react';
import KineticReversalHero from '@/components/KineticReversalHero';
import KovelSpinner from '@/components/KovelSpinner';
import BlogTeaser from '@/components/shared/BlogTeaser';
import ComparisonTable from '@/components/shared/ComparisonTable';
import ContactModal from '@/components/shared/ContactModal';
import CTASection from '@/components/shared/CTASection';
import DiscoveryRisk from '@/components/shared/DiscoveryRisk';
import FAQ from '@/components/shared/FAQ';
import FallingGavel from '@/components/shared/FallingGavel';
import Features from '@/components/shared/Features';
import Footer from '@/components/shared/Footer';
import HowItWorks from '@/components/shared/HowItWorks';
import Management from '@/components/shared/Management';
import Nav from '@/components/shared/Nav';
import Pricing from '@/components/shared/Pricing';
import ScrollProgress from '@/components/shared/ScrollProgress';
import StatsBar from '@/components/shared/StatsBar';
import Testimonials from '@/components/shared/Testimonials';

export default function Home() {
  const [modalOpen, setModalOpen] = useState(false);
  const openModal = useCallback(() => setModalOpen(true), []);
  const closeModal = useCallback(() => setModalOpen(false), []);

  return (
    <>
      {/* AgentSpinner — KovelAI hydration overlay */}
      <KovelSpinner />
      {/* WCAG 2.4.1 Skip Navigation */}
      <a href="#main-content" className="skip-nav">
        Skip to main content
      </a>
      <ScrollProgress />
      <Nav onOpenModal={openModal} />
      <main id="main-content">
        <KineticReversalHero onOpenModal={openModal} />
        <StatsBar />
        <DiscoveryRisk />
        <Features />
        <HowItWorks />
        <Testimonials />
        <ComparisonTable />
        <Pricing onOpenModal={openModal} />
        <FallingGavel onOpenModal={openModal} />
        <FAQ />
        <Management />
        <BlogTeaser />
        <CTASection onOpenModal={openModal} />
      </main>
      <Footer onOpenModal={openModal} />
      <ContactModal isOpen={modalOpen} onClose={closeModal} />
    </>
  );
}

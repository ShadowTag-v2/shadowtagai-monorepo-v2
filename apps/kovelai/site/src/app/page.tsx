'use client';

import { useCallback, useState } from 'react';
import BlogTeaser from '@/components/shared/BlogTeaser';
import ComparisonTable from '@/components/shared/ComparisonTable';
import ContactModal from '@/components/shared/ContactModal';
import CTASection from '@/components/shared/CTASection';
import DiscoveryRisk from '@/components/shared/DiscoveryRisk';
import FAQ from '@/components/shared/FAQ';
import Features from '@/components/shared/Features';
import Footer from '@/components/shared/Footer';
import Hero from '@/components/shared/Hero';
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
      {/* WCAG 2.4.1 Skip Navigation */}
      <a href="#main-content" className="skip-nav">
        Skip to main content
      </a>
      <ScrollProgress />
      <Nav onOpenModal={openModal} />
      <main id="main-content">
        <Hero />
        <StatsBar />
        <DiscoveryRisk />
        <Features />
        <HowItWorks />
        <Testimonials />
        <ComparisonTable />
        <Pricing onOpenModal={openModal} />
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

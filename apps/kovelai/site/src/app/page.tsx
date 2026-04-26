'use client';

import { useCallback, useState } from 'react';
import BlogTeaser from '@/components/BlogTeaser';
import ComparisonTable from '@/components/ComparisonTable';
import ContactModal from '@/components/ContactModal';
import CTASection from '@/components/CTASection';
import DiscoveryRisk from '@/components/DiscoveryRisk';
import FAQ from '@/components/FAQ';
import Features from '@/components/Features';
import Footer from '@/components/Footer';
import Hero from '@/components/Hero';
import HowItWorks from '@/components/HowItWorks';
import Management from '@/components/Management';
import Nav from '@/components/Nav';
import Pricing from '@/components/Pricing';
import ScrollProgress from '@/components/ScrollProgress';
import StatsBar from '@/components/StatsBar';
import Testimonials from '@/components/Testimonials';

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

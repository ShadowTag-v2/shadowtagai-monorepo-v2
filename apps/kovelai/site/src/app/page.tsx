'use client';

import Nav from '@/components/Nav';
import Hero from '@/components/Hero';
import StatsBar from '@/components/StatsBar';
import DiscoveryRisk from '@/components/DiscoveryRisk';
import Features from '@/components/Features';
import HowItWorks from '@/components/HowItWorks';
import Testimonials from '@/components/Testimonials';
import ComparisonTable from '@/components/ComparisonTable';
import Pricing from '@/components/Pricing';
import FAQ from '@/components/FAQ';
import Management from '@/components/Management';
import BlogTeaser from '@/components/BlogTeaser';
import CTASection from '@/components/CTASection';
import Footer from '@/components/Footer';
import ContactModal from '@/components/ContactModal';
import ScrollProgress from '@/components/ScrollProgress';

export default function Home() {
  return (
    <>
      <ScrollProgress />
      <Nav />
      <main>
        <Hero />
        <StatsBar />
        <DiscoveryRisk />
        <Features />
        <HowItWorks />
        <Testimonials />
        <ComparisonTable />
        <Pricing />
        <FAQ />
        <Management />
        <BlogTeaser />
        <CTASection />
      </main>
      <Footer />
      <ContactModal />
    </>
  );
}

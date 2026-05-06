"use client";

import { NavBar } from "@/components/home/NavBar";
import { HeroSection } from "@/components/home/HeroSection";
import { StatsBar } from "@/components/home/StatsBar";
import { PlatformSection } from "@/components/home/PlatformSection";
import { HowItWorks } from "@/components/home/HowItWorks";
import { ModelRouting } from "@/components/home/ModelRouting";
import { PricingSection } from "@/components/home/PricingSection";
import { EmailCapture } from "@/components/home/EmailCapture";
import { HeppnerSection } from "@/components/home/HeppnerSection";
import { AboutSection } from "@/components/home/AboutSection";
import { Footer } from "@/components/home/Footer";
import { ScrollProgress } from "@/components/home/ScrollProgress";

export default function Home() {
  return (
    <>
      <ScrollProgress />
      <NavBar />
      <main>
        <HeroSection />
        <StatsBar />
        <PlatformSection />
        <HowItWorks />
        <ModelRouting />
        <PricingSection />
        <EmailCapture />
        <HeppnerSection />
        <AboutSection />
      </main>
      <Footer />
    </>
  );
}

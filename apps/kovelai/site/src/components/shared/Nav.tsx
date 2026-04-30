'use client';
import Image from 'next/image';
import { useEffect, useState } from 'react';

interface NavProps {
  onOpenModal: () => void;
}

export default function Nav({ onOpenModal }: NavProps) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <nav
      className={`glass-nav fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'shadow-ambient' : ''}`}
    >
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <a
          href="/"
          className="flex items-center gap-2 text-xl font-bold tracking-tight text-[#d7e3fc]"
        >
          <Image
            src="/images/logo-s.jpeg"
            alt="KovelAI logo"
            width={32}
            height={32}
            className="rounded-sm"
          />
          KovelAI
        </a>
        <ul className="hidden md:flex items-center gap-6 text-sm">
          {['Discovery Risk', 'Features', 'Pricing', 'How It Works', 'FAQ'].map((t) => (
            <li key={t}>
              <a
                href={`#${t.toLowerCase().replace(/ /g, '-')}`}
                className="text-[#d0c5b5] hover:text-[#d7e3fc] transition-colors"
              >
                {t}
              </a>
            </li>
          ))}
        </ul>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onOpenModal}
            className="btn-gold text-sm py-2 px-4 hidden sm:inline-flex"
          >
            Contact Sales
          </button>
          <button
            type="button"
            className="md:hidden text-[#d7e3fc] text-2xl"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle navigation"
          >
            ☰
          </button>
        </div>
      </div>
      {mobileOpen && (
        <div className="md:hidden px-4 pb-4 flex flex-col gap-3 text-sm">
          {['Discovery Risk', 'Features', 'Pricing', 'How It Works', 'FAQ'].map((t) => (
            <a
              key={t}
              href={`#${t.toLowerCase().replace(/ /g, '-')}`}
              onClick={() => setMobileOpen(false)}
              className="text-[#d0c5b5] hover:text-[#d7e3fc] py-1"
            >
              {t}
            </a>
          ))}
        </div>
      )}
    </nav>
  );
}

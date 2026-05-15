'use client';

import { useEffect, useState } from 'react';

/* ===== Data ===== */
const NAV_ITEMS = [
  { label: 'Products', href: '/products/', children: [] },
  {
    label: 'Media & Events',
    href: '#',
    children: [
      { label: 'Media Coverage', href: '/news-events/media-coverage/' },
      { label: 'Events', href: '/news-events/events/' },
      { label: 'Media Inquiries', href: '/media-inquiries/' },
    ],
  },
  {
    label: 'Investors',
    href: '#',
    children: [
      { label: 'Stock Information', href: '/stock/' },
      { label: 'Press Releases', href: '/news-events/press-releases/' },
      { label: 'SEC Filings', href: '/sec-filings/' },
      { label: 'Company Presentation', href: '/about-us/company-presentation/' },
    ],
  },
  {
    label: 'Contact',
    href: '#',
    children: [
      { label: 'Sales Inquiries', href: '/contact-sales-inquiries/' },
      { label: 'IR Contact', href: '/contact-ir/' },
    ],
  },
  { label: 'Careers', href: 'https://apply.workable.com/unusual-machines/', children: [] },
  {
    label: 'About Us',
    href: '#',
    children: [
      { label: 'Our Story', href: '/about-us/' },
      { label: 'Leadership', href: '/about-us/leadership/' },
      { label: 'Company Presentation', href: '/about-us/company-presentation/' },
    ],
  },
];

const RECENT_NEWS = [
  'Unusual Machines Secures $5M+ Order from Powerus for Counter-UAS Systems',
  'Unusual Machines Appoints Chadd Cole as Vice President of FP&A',
  'Unusual Machines Accelerates Motor Factory Output at Orlando Campus',
];

const QUICK_LINKS = [
  {
    label: 'Quotes and Charts',
    href: '/stock/',
    icon: 'https://cdn-sites-assets.mziq.com/wp-content/uploads/sites/1374/2024/06/icon-charts.png',
  },
  {
    label: 'Investor Presentation',
    href: '/about-us/company-presentation/',
    icon: 'https://cdn-sites-assets.mziq.com/wp-content/uploads/sites/1374/2024/06/Group-40.png',
  },
  {
    label: 'Email Alerts',
    href: '/email-alerts/',
    icon: 'https://cdn-sites-assets.mziq.com/wp-content/uploads/sites/1374/2024/06/feather_mail-1.png',
  },
  {
    label: 'IR Contact',
    href: '/contact-ir/',
    icon: 'https://cdn-sites-assets.mziq.com/wp-content/uploads/sites/1374/2024/06/Vector-33.png',
  },
];

const SOCIAL_LINKS = [
  {
    label: 'facebook',
    href: 'https://www.facebook.com/profile.php?id=61556734025184',
    icon: 'https://cdn-sites-assets.mziq.com/wp-content/themes/mziq_unusual_machines/img/social-media/icon-facebook.png',
  },
  {
    label: 'instagram',
    href: 'https://www.instagram.com/unusualmachinesinc/',
    icon: 'https://cdn-sites-assets.mziq.com/wp-content/themes/mziq_unusual_machines/img/social-media/icon-instagram.png',
  },
  {
    label: 'linkedin',
    href: 'https://www.linkedin.com/company/unusual-machines',
    icon: 'https://cdn-sites-assets.mziq.com/wp-content/themes/mziq_unusual_machines/img/social-media/icon-linkedin.png',
  },
  {
    label: 'twitter',
    href: 'https://twitter.com/',
    icon: 'https://cdn-sites-assets.mziq.com/wp-content/themes/mziq_unusual_machines/img/social-media/icon-twitter.png',
  },
];

const ArrowRight = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" className="news-item__arrow">
    <path
      d="M4 10H16M16 10L11 5M16 10L11 15"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const ChevronDown = () => (
  <svg width="10" height="6" viewBox="0 0 10 6" fill="none" style={{ marginLeft: 2 }}>
    <path
      d="M1 1L5 5L9 1"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

/* ===== Component ===== */
export default function Home() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 80);
    window.addEventListener('scroll', handler, { passive: true });
    return () => window.removeEventListener('scroll', handler);
  }, []);

  return (
    <>
      {/* ===== HEADER ===== */}
      <header className={`header ${scrolled ? 'header--scrolled' : ''}`}>
        <div className="header__inner">
          <a href="/" className="header__logo">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="https://cdn-sites-assets.mziq.com/wp-content/uploads/sites/1374/2024/06/logo.png"
              alt="Unusual Machines"
              width={166}
              height={41}
            />
          </a>

          <nav className="nav" aria-label="Main navigation">
            {NAV_ITEMS.map((item) => (
              <div className="nav__item" key={item.label}>
                <a className="nav__link" href={item.href}>
                  {item.label}
                  {item.children.length > 0 && <ChevronDown />}
                </a>
                {item.children.length > 0 && (
                  <div className="nav__dropdown">
                    {item.children.map((child) => (
                      <a key={child.label} className="nav__dropdown-link" href={child.href}>
                        {child.label}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </nav>

          <div className="header__right">
            <div className="header__a11y">
              <button aria-label="Decrease font size">A-</button>
              <button aria-label="Increase font size">A+</button>
              <button aria-label="Toggle contrast">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                  <circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" strokeWidth="1.5" />
                  <path d="M8 2a6 6 0 0 1 0 12V2z" />
                </svg>{' '}
                Contrast
              </button>
              <a href="/accessibility/">Accessibility</a>
            </div>
            <a href="/contact-sales-inquiries/" className="header__cta">
              CONTACT SALES
            </a>
            <button className="mobile-toggle" aria-label="Toggle menu">
              <span />
              <span />
              <span />
            </button>
          </div>
        </div>
      </header>

      {/* ===== HERO ===== */}
      <section className="hero" id="hero">
        <div className="hero__bg" aria-hidden="true" />
        <div className="hero__overlay" aria-hidden="true" />
        <div className="hero__content">
          <div className="hero__text">
            <h1 className="hero__title">Here to serve the American drone industry.</h1>
          </div>
          <div className="hero__stock">
            <div className="hero__ticker-label">NYSE: UMAC</div>
            <div className="hero__price">$14.65</div>
            <div className="hero__change hero__change--down">▼ $-1.48</div>
            <div className="hero__volume">
              <span className="hero__volume-label">Volume</span>
              <span>4,865,874</span>
            </div>
            <div className="hero__date">04/24/2026 4:10 PM</div>
          </div>
        </div>
      </section>

      {/* ===== HIGHLIGHTS / NEWS ===== */}
      <section className="highlights" id="highlights">
        <div className="container">
          <h2 className="section-title">Recent News</h2>
          <div className="highlights__grid">
            {RECENT_NEWS.map((headline, i) => (
              <button key={i} className="news-item">
                <span>{headline}</span>
                <ArrowRight />
              </button>
            ))}
          </div>
          <div className="highlights__footer">
            <a href="/press-releases/" className="see-all-btn">
              See all
            </a>
          </div>
        </div>
      </section>

      {/* ===== QUICK LINKS ===== */}
      <section className="quick-links" id="quick-links">
        <div className="quick-links__layout">
          <div className="quick-links__title-col">
            <h2>Quick Links</h2>
          </div>
          <div className="quick-links__cards-col">
            <div className="quick-links__cards-overlay" aria-hidden="true" />
            <div className="quick-links__grid">
              {QUICK_LINKS.map((link) => (
                <a key={link.label} href={link.href} className="quick-link-card">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={link.icon}
                    alt={link.label}
                    className="quick-link-card__icon"
                    width={50}
                    height={60}
                  />
                  <span className="quick-link-card__label">{link.label}</span>
                </a>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ===== EVENTS ===== */}
      <section className="events" id="events">
        <div className="container">
          <h2 className="section-title">Upcoming Events</h2>
          <p className="events__empty">No upcoming events!</p>
          <div className="events__footer">
            <a href="/company-events/" className="see-all-btn">
              See all
            </a>
          </div>
        </div>
      </section>

      {/* ===== CONTACT ===== */}
      <section className="contact" id="contact">
        <div className="contact__overlay" aria-hidden="true" />
        <div className="contact__content container">
          <h2 className="contact__title">Contact</h2>
          <div className="contact__grid">
            {/* Left: Contact Info */}
            <div className="contact__info">
              <h3>Investor Contact</h3>
              <p>You can talk to our IR team through the information below.</p>
              <p>
                Email: investors@unusualmachines.com
                <br />
                Christine Petraglia
                <br />
                CS Investor Relations
                <br />
                IR &amp; Market Strategies
                <br />
                T: 917-633-8980
              </p>

              <h3 style={{ marginTop: '32px' }}>Media Inquiries</h3>
              <p>
                media@unusualmachines.com
                <br />
                917-771-7693
              </p>
            </div>

            {/* Right: Email Alerts Form */}
            <div className="contact__form-card">
              <h2>Email Alerts</h2>
              <input
                type="email"
                className="contact__input"
                placeholder="Email*"
                required
                aria-label="Email address"
              />
              <input
                type="text"
                className="contact__input"
                placeholder="First Name"
                aria-label="First name"
              />
              <input
                type="text"
                className="contact__input"
                placeholder="Last Name"
                aria-label="Last name"
              />
              <input
                type="text"
                className="contact__input"
                placeholder="Company"
                aria-label="Company"
              />
              <div className="contact__checkbox-group">
                <input type="checkbox" id="press-releases" />
                <label htmlFor="press-releases">Press Releases</label>
              </div>
              <button type="submit" className="contact__submit">
                Subscribe
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ===== FOOTER ===== */}
      <footer className="footer">
        <div className="footer__inner">
          <span className="footer__copy">Unusual Machines - All Rights Reserved</span>
          <div className="footer__center">
            {SOCIAL_LINKS.map((social) => (
              <a
                key={social.label}
                href={social.href}
                className="footer__social-link"
                aria-label={social.label}
                target="_blank"
                rel="noopener noreferrer"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={social.icon} alt={social.label} width={18} height={18} />
              </a>
            ))}
          </div>
          <span className="footer__powered">
            <a href="https://www.mzgroup.com/" target="_blank" rel="noopener noreferrer">
              Powered by MZ
            </a>
          </span>
        </div>
      </footer>
    </>
  );
}

/* ═══════════════════════════════════════════════════════════
   ShadowTag AI — Product Pitch Site
   JavaScript: scroll animations, particles, nav
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  /* ─── HEADER SCROLL ─── */
  const header = document.getElementById('site-header');
  let lastScroll = 0;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (y > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
    lastScroll = y;
  }, { passive: true });

  /* ─── MOBILE NAV ─── */
  const hamburger = document.getElementById('hamburger-menu');
  const mainMenu = document.querySelector('.header__content__mainMenu');
  const closeMenu = document.getElementById('close-menu');

  if (hamburger && mainMenu) {
    hamburger.addEventListener('click', () => {
      mainMenu.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
    closeMenu?.addEventListener('click', () => {
      mainMenu.classList.remove('active');
      document.body.style.overflow = '';
    });
    // Close on nav link click (mobile)
    mainMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mainMenu.classList.remove('active');
        document.body.style.overflow = '';
      });
    });
  }

  /* ─── SCROLL-DRIVEN FADE-IN ─── */
  const animElements = document.querySelectorAll(
    '.homeBanner__content__text, .homeBanner__content__quotations, ' +
    '.news-item, .product-card, .arch-card, .metric-block, .business-card'
  );

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
      if (entry.isIntersecting) {
        // Stagger animation by sibling index
        const parent = entry.target.parentElement;
        const siblings = parent ? Array.from(parent.children) : [];
        const siblingIndex = siblings.indexOf(entry.target);
        const delay = Math.min(siblingIndex * 100, 500);

        setTimeout(() => {
          entry.target.classList.add('animate-in');
        }, delay);

        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  });

  animElements.forEach(el => observer.observe(el));

  /* ─── FLOATING PARTICLES ─── */
  const particlesContainer = document.getElementById('particles');
  if (particlesContainer) {
    const PARTICLE_COUNT = 30;
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      const x = Math.random() * 100;
      const duration = 8 + Math.random() * 12;
      const delay = Math.random() * 15;
      const size = 2 + Math.random() * 3;
      const hue = Math.random() > 0.7 ? '280' : '185';

      particle.style.cssText = `
        left: ${x}%;
        width: ${size}px;
        height: ${size}px;
        animation-duration: ${duration}s;
        animation-delay: ${delay}s;
        background: hsl(${hue}, 100%, 70%);
        box-shadow: 0 0 ${size * 3}px hsl(${hue}, 100%, 50%);
      `;
      particlesContainer.appendChild(particle);
    }
  }

  /* ─── COUNTER ANIMATION ─── */
  const counters = document.querySelectorAll('.metric-block__value[data-count]');
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseInt(el.getAttribute('data-count'), 10);
        const duration = 2000;
        const start = performance.now();

        const animateCount = (now) => {
          const elapsed = now - start;
          const progress = Math.min(elapsed / duration, 1);
          const eased = 1 - Math.pow(1 - progress, 3);
          const current = Math.round(eased * target);
          el.textContent = current.toLocaleString();
          if (progress < 1) requestAnimationFrame(animateCount);
        };
        requestAnimationFrame(animateCount);
        counterObserver.unobserve(el);
      }
    });
  }, { threshold: 0.5 });
  counters.forEach(c => counterObserver.observe(c));

  /* ─── SMOOTH SCROLL FOR NAV LINKS ─── */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const targetId = anchor.getAttribute('href');
      if (targetId === '#') return;
      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        const headerOffset = 100;
        const y = target.getBoundingClientRect().top + window.scrollY - headerOffset;
        window.scrollTo({ top: y, behavior: 'smooth' });
      }
    });
  });

  /* ─── FORM HANDLER ─── */
  const form = document.getElementById('earlyAccessForm');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      const originalText = btn.textContent;
      btn.textContent = '✓ Request Sent';
      btn.style.background = 'rgba(76, 175, 80, 0.2)';
      btn.style.borderColor = '#4caf50';
      btn.style.color = '#4caf50';
      btn.style.boxShadow = 'none';
      btn.disabled = true;
      setTimeout(() => {
        btn.textContent = originalText;
        btn.style.cssText = '';
        btn.disabled = false;
        form.reset();
      }, 3000);
    });
  }

  console.log('%cShadowTag AI', 'color: #00e5ff; font-size: 16px; font-weight: bold; font-family: monospace;');
  console.log('%cSovereign AI Infrastructure · shadowtag-omega-v4', 'color: #8b8ba0; font-size: 11px; font-family: monospace;');
});

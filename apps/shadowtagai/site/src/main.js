import './style.css';

// ═══ SCROLL PROGRESS ═══
const scrollProgress = document.getElementById('scrollProgress');
if (scrollProgress) {
  window.addEventListener(
    'scroll',
    () => {
      const pct = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
      scrollProgress.style.transform = `scaleX(${Math.min(pct, 1)})`;
      scrollProgress.style.width = '100%';
    },
    { passive: true },
  );
}

// ═══ CSS PARTICLE FIELD ═══
const particleContainer = document.getElementById('particles');
if (particleContainer) {
  for (let i = 0; i < 30; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.left = `${Math.random() * 100}%`;
    p.style.animationDuration = `${8 + Math.random() * 12}s`;
    p.style.animationDelay = `${Math.random() * 10}s`;
    p.style.width = p.style.height = `${1 + Math.random() * 2}px`;
    particleContainer.appendChild(p);
  }
}

// ═══ REVEAL ON SCROLL ═══
const reveals = document.querySelectorAll('.reveal');
if (reveals.length) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) e.target.classList.add('visible');
      });
    },
    { threshold: 0.1 },
  );
  reveals.forEach((el) => observer.observe(el));
}

// ═══ CONTACT MODAL ═══
const modal = document.getElementById('contactModal');
const toast = document.getElementById('toast');

window.openContactModal = () => {
  if (modal) {
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
  }
};
window.closeContactModal = () => {
  if (modal) {
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
  }
};
if (modal) {
  modal.addEventListener('click', (e) => {
    if (e.target === modal) window.closeContactModal();
  });
}

const form = document.getElementById('contactForm');
if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = new FormData(form);
    if (data.get('_honey')) return;
    try {
      await fetch(form.action, { method: 'POST', body: data });
      window.closeContactModal();
      if (toast) {
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 4000);
      }
      form.reset();
    } catch (err) {
      /* silent */
    }
  });
}

// ═══ NAV SCROLL EFFECT ═══
const nav = document.querySelector('.nav');
if (nav) {
  window.addEventListener(
    'scroll',
    () => {
      nav.style.background =
        window.scrollY > 50 ? 'rgba(15, 19, 31, 0.98)' : 'rgba(15, 19, 31, 0.85)';
    },
    { passive: true },
  );
}

// ═══ MOBILE NAV ═══
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');
if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
  });
}

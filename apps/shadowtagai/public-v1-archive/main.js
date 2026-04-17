// KovelAI — Minimal Interactive Layer
document.addEventListener('DOMContentLoaded', () => {
    // Mobile nav toggle
    const toggle = document.getElementById('nav-toggle');
    const links = document.getElementById('nav-links');
    if (toggle && links) {
        toggle.addEventListener('click', () => {
            links.style.display = links.style.display === 'flex' ? 'none' : 'flex';
            links.style.flexDirection = 'column';
            links.style.position = 'absolute';
            links.style.top = '72px';
            links.style.left = '0';
            links.style.right = '0';
            links.style.background = 'rgba(6,6,16,0.98)';
            links.style.padding = '24px 32px';
            links.style.gap = '16px';
            links.style.borderBottom = '1px solid rgba(255,255,255,0.06)';
        });
    }

    // Nav scroll effect
    const nav = document.getElementById('main-nav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 80) {
            nav.style.background = 'rgba(6,6,16,0.95)';
        } else {
            nav.style.background = 'rgba(6,6,16,0.88)';
        }
    });

    // Pilot form
    const form = document.getElementById('pilot-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = document.getElementById('pilot-submit');
            btn.innerHTML = '<span>✓ Request Submitted</span>';
            btn.style.background = '#10b981';
            btn.disabled = true;
            setTimeout(() => {
                btn.innerHTML = '<span>Request Pilot Access</span>';
                btn.style.background = '';
                btn.disabled = false;
                form.reset();
            }, 3000);
        });
    }

    // Intersection Observer for scroll animations
    const cards = document.querySelectorAll('.mech-card, .shield-card, .seu-card, .danger-card, .safe-card, .price-card, .guardrail-item');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    cards.forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = `opacity 0.5s ease ${i * 0.05}s, transform 0.5s ease ${i * 0.05}s`;
        observer.observe(card);
    });
});

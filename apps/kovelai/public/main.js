// KovelAI — "The Chambers" Interactive Layer
// BARBRI Authority × Aman Resorts Serenity

document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------
    // 1. Navigation: scroll state + mobile toggle
    // -------------------------------------------
    const nav = document.getElementById('main-nav');
    const toggle = document.getElementById('nav-toggle');
    const links = document.getElementById('nav-links');

    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const current = window.scrollY;
        if (current > 60) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
        lastScroll = current;
    }, { passive: true });

    if (toggle && links) {
        toggle.addEventListener('click', () => {
            links.classList.toggle('open');
            toggle.classList.toggle('active');
        });
        // Close mobile nav when a link is clicked
        links.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                links.classList.remove('open');
                toggle.classList.remove('active');
            });
        });
    }

    // -------------------------------------------
    // 2. Scroll Reveal: IntersectionObserver
    // -------------------------------------------
    const revealElements = document.querySelectorAll('.reveal');
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                // Stagger children
                const parent = entry.target.closest('.bento-grid, .testimonial-grid, .pricing-grid, .problem-stats');
                if (parent) {
                    const siblings = parent.querySelectorAll('.reveal');
                    const index = Array.from(siblings).indexOf(entry.target);
                    entry.target.style.transitionDelay = `${index * 0.1}s`;
                }
                entry.target.classList.add('visible');
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.12,
        rootMargin: '0px 0px -60px 0px'
    });

    revealElements.forEach(el => revealObserver.observe(el));

    // -------------------------------------------
    // 3. Animated Counter (stat values)
    // -------------------------------------------
    const statValues = document.querySelectorAll('.stat-value');
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateValue(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    statValues.forEach(el => counterObserver.observe(el));

    function animateValue(element) {
        const text = element.textContent;
        const match = text.match(/([\$]?)([\d,.]+)(.*)/);
        if (!match) return;

        const prefix = match[1];
        const numStr = match[2].replace(/,/g, '');
        const suffix = match[3];
        const target = parseFloat(numStr);
        const isFloat = numStr.includes('.');
        const duration = 1200;
        const start = performance.now();

        function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = target * eased;

            if (isFloat) {
                element.textContent = prefix + current.toFixed(1) + suffix;
            } else {
                element.textContent = prefix + Math.floor(current).toLocaleString() + suffix;
            }

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                element.textContent = text; // Restore exact original
            }
        }
        requestAnimationFrame(update);
    }

    // -------------------------------------------
    // 4. Form submission
    // -------------------------------------------
    const form = document.getElementById('pilot-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = document.getElementById('pilot-submit');
            const originalHTML = btn.innerHTML;

            // Success state
            btn.innerHTML = '<span>✓ Request Submitted</span>';
            btn.style.background = '#2DD4BF';
            btn.style.backgroundImage = 'none';
            btn.disabled = true;

            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.style.background = '';
                btn.style.backgroundImage = '';
                btn.disabled = false;
                form.reset();
            }, 3000);
        });
    }

    // -------------------------------------------
    // 5. Smooth scroll for anchor links
    // -------------------------------------------
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                const navHeight = nav.offsetHeight;
                const targetPosition = target.getBoundingClientRect().top + window.scrollY - navHeight - 20;
                window.scrollTo({ top: targetPosition, behavior: 'smooth' });
            }
        });
    });

    // -------------------------------------------
    // 6. Parallax hero image (subtle)
    // -------------------------------------------
    const heroBg = document.querySelector('.hero-bg img');
    if (heroBg && window.matchMedia('(min-width: 768px)').matches) {
        window.addEventListener('scroll', () => {
            const scrolled = window.scrollY;
            if (scrolled < window.innerHeight) {
                heroBg.style.transform = `scale(1.05) translateY(${scrolled * 0.15}px)`;
            }
        }, { passive: true });
    }
});

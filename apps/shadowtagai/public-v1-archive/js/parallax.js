// ES6 Module parallax.js
// Handles scroll-triggered kinetic parallax for the hero layer

export function initHeroParallax() {
    const hero = document.querySelector('.hero');
    if (!hero) return;

    // Respect reduced-motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const video = hero.querySelector('.hero-video-bg');
    const particles = hero.querySelector('.hero-particles-canvas');
    const content = hero.querySelector('.hero-content');
    const grain = hero.querySelector('.hero-grain');
    const vignette = hero.querySelector('.hero-video-vignette');

    let ticking = false;
    let lastScrollY = 0;

    function lerp(start, end, factor) {
        return start + (end - start) * factor;
    }

    // Track smoothed values for buttery motion
    let smoothY = 0;

    function onScroll() {
        lastScrollY = window.scrollY;
        if (!ticking) {
            requestAnimationFrame(updateParallax);
            ticking = true;
        }
    }

    function updateParallax() {
        const heroHeight = hero.offsetHeight;
        // Normalize scroll to 0-1 range within hero bounds
        const scrollRatio = Math.min(lastScrollY / heroHeight, 1.5);
        smoothY = lerp(smoothY, scrollRatio, 0.12);

        // Layer 1: Video moves slowest (depth illusion)
        if (video) {
            const videoShift = smoothY * 60; // max 60px
            const videoScale = 1 + smoothY * 0.05; // subtle zoom
            video.style.transform = `translate3d(0, ${videoShift}px, 0) scale(${videoScale})`;
        }

        // Layer 2: Particles move at medium speed
        if (particles) {
            const particleShift = smoothY * 35;
            particles.style.transform = `translate3d(0, ${particleShift}px, 0)`;
        }

        // Layer 3: Content moves fastest (foreground)
        if (content) {
            const contentShift = smoothY * -20;
            const contentOpacity = Math.max(1 - smoothY * 0.6, 0);
            content.style.transform = `translate3d(0, ${contentShift}px, 0)`;
            content.style.opacity = contentOpacity;
        }

        // Grain and vignette: subtle scale
        if (grain) {
            grain.style.transform = `translate3d(0, ${smoothY * 20}px, 0)`;
        }
        if (vignette) {
            const vignetteOpacity = Math.min(1 + smoothY * 0.3, 1.3);
            vignette.style.opacity = vignetteOpacity;
        }

        ticking = false;
    }

    // Use passive listener for performance
    window.addEventListener('scroll', onScroll, { passive: true });

    // Also handle resize to recalculate hero height
    window.addEventListener('resize', () => {
        if (!ticking) {
            requestAnimationFrame(updateParallax);
            ticking = true;
        }
    }, { passive: true });
}

// Auto-initialize if DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHeroParallax);
} else {
    initHeroParallax();
}

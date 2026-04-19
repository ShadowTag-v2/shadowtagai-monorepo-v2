/**
 * Scroll-Driven Frame Animation Controller
 *
 * Scrubs through Veo-extracted video frames based on scroll position.
 * Produces an Apple-style scroll-driven video effect.
 *
 * Usage:
 *   1. Extract frames: python scripts/veo_pipeline.py --extract video.mp4 --fps 30
 *   2. Frames land in public/frames/{video_stem}/frame_XXXX.png
 *   3. This script preloads and scrubs them on scroll.
 */

(function () {
  'use strict';

  // ── Configuration ──
  const FRAME_DIR = 'frames/hero_drift_0';
  const FRAME_PREFIX = 'frame_';
  const FRAME_EXT = '.png';
  const TOTAL_FRAMES = 80; // 8s video @ 10fps
  const FRAME_DIGITS = 4;

  // ── State ──
  const canvas = document.getElementById('scroll-canvas');
  const ctx = canvas ? canvas.getContext('2d') : null;
  const images = [];
  let loaded = 0;
  let currentFrame = 0;
  let rafId = null;

  // ── Frame URL builder ──
  function frameUrl(index) {
    const num = String(index + 1).padStart(FRAME_DIGITS, '0');
    return `${FRAME_DIR}/${FRAME_PREFIX}${num}${FRAME_EXT}`;
  }

  // ── Preload all frames ──
  function preloadFrames() {
    for (let i = 0; i < TOTAL_FRAMES; i++) {
      const img = new Image();
      img.src = frameUrl(i);
      img.addEventListener('load', () => {
        loaded++;
        if (loaded === 1) {
          resizeCanvas();
          drawFrame(0);
        }
        if (loaded === TOTAL_FRAMES) {
          console.log(`[ScrollFrames] All ${TOTAL_FRAMES} frames preloaded`);
        }
      });
      img.addEventListener('error', () => {
        console.warn(`[ScrollFrames] Failed to load: ${frameUrl(i)}`);
      });
      images.push(img);
    }
  }

  // ── Canvas sizing ──
  function resizeCanvas() {
    if (!canvas) return;
    canvas.width = window.innerWidth * window.devicePixelRatio;
    canvas.height = window.innerHeight * window.devicePixelRatio;
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    drawFrame(currentFrame);
  }

  // ── Draw a specific frame ──
  function drawFrame(index) {
    if (!ctx || !images[index] || !images[index].complete) return;
    const img = images[index];

    // Cover-fit the image to canvas
    const canvasAspect = canvas.width / canvas.height;
    const imgAspect = img.naturalWidth / img.naturalHeight;

    let sx = 0, sy = 0, sw = img.naturalWidth, sh = img.naturalHeight;

    if (imgAspect > canvasAspect) {
      // Image is wider — crop sides
      sw = img.naturalHeight * canvasAspect;
      sx = (img.naturalWidth - sw) / 2;
    } else {
      // Image is taller — crop top/bottom
      sh = img.naturalWidth / canvasAspect;
      sy = (img.naturalHeight - sh) / 2;
    }

    ctx.drawImage(img, sx, sy, sw, sh, 0, 0, canvas.width, canvas.height);
  }

  // ── Scroll handler ──
  function onScroll() {
    const container = document.querySelector('.scroll-video-container');
    if (!container) return;

    const rect = container.getBoundingClientRect();
    const containerHeight = container.offsetHeight - window.innerHeight;
    const scrolled = -rect.top;
    const progress = Math.max(0, Math.min(1, scrolled / containerHeight));

    const targetFrame = Math.floor(progress * (TOTAL_FRAMES - 1));

    if (targetFrame !== currentFrame) {
      currentFrame = targetFrame;
      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => drawFrame(currentFrame));
    }
  }

  // ── Intersection Observer for fade-in animations ──
  function initFadeAnimations() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );

    document.querySelectorAll('.fade-in').forEach((el) => observer.observe(el));
  }

  // ── Init ──
  function init() {
    if (!canvas || !ctx) {
      console.warn('[ScrollFrames] Canvas not found, using fallback');
      return;
    }

    preloadFrames();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', resizeCanvas);
    initFadeAnimations();

    console.log('[ScrollFrames] Controller initialized');
  }

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

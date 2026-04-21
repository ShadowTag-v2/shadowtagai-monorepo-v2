/**
 * Scroll-Driven Frame Animation Controller v2
 *
 * Features:
 *   - Scroll-scrub through Veo-extracted video frames (Apple-style)
 *   - Lazy-loading with IntersectionObserver (Task #11)
 *   - Progress bar overlay (Task #17)
 *   - WebP format support with PNG fallback (Task #7)
 *   - Retina/HiDPI canvas rendering (Task #19)
 *   - A/B video tag fallback for low-power devices (Task #21)
 *   - Service worker registration (Task #8)
 *
 * Usage:
 *   1. Extract frames: python scripts/veo_pipeline.py --extract video.mp4 --fps 10
 *   2. Convert: cwebp -q 80 frame.png -o frame.webp
 *   3. Drop this script on any page with <canvas id="scroll-canvas">
 */

(() => {
  // ── Configuration ──
  const CONFIG = {
    frameDir: 'frames/hero_drift_0',
    webpDir: 'frames/hero_drift_0_webp',
    framePrefix: 'frame_',
    totalFrames: 48,
    frameDigits: 4,
    lazyThreshold: 0.05,
    enableWebP: false, // JPG frames from Veo extraction
    enableRetina: true,
    videoFallbackSrc: '/videos/hero-bg.mp4',
    lowPowerThreshold: 4, // CPU cores threshold for fallback
  };

  // ── State ──
  const canvas = document.getElementById('scroll-canvas');
  const ctx = canvas ? canvas.getContext('2d') : null;
  const images = [];
  let loaded = 0;
  let currentFrame = 0;
  let rafId = null;
  let useVideoFallback = false;
  let progressBar = null;

  // ── Detect WebP support ──
  function supportsWebP() {
    const el = document.createElement('canvas');
    return el.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  }

  // ── A/B: Detect low-power device → video fallback (#21) ──
  function shouldUseVideoFallback() {
    const cores = navigator.hardwareConcurrency || 4;
    const isMobile = /Mobi|Android|iPhone/i.test(navigator.userAgent);
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    return cores < CONFIG.lowPowerThreshold || (isMobile && cores <= 4) || prefersReducedMotion;
  }

  // ── Create video fallback element (#21) ──
  function createVideoFallback() {
    const container = document.querySelector('.scroll-video-sticky');
    if (!container || !canvas) return;

    const video = document.createElement('video');
    video.src = CONFIG.videoFallbackSrc;
    video.autoplay = true;
    video.muted = true;
    video.loop = true;
    video.playsInline = true;
    video.poster = '/images/posters/hero-drift-compressed.webp';
    video.setAttribute('loading', 'lazy');
    video.style.cssText = 'width:100%;height:100%;object-fit:cover;opacity:0.85;';
    video.id = 'scroll-video-fallback';

    canvas.style.display = 'none';
    container.insertBefore(video, container.firstChild);
    console.log('[ScrollFrames] Using video tag fallback (low-power device)');
    return true;
  }

  // ── Frame URL builder with WebP/PNG detection ──
  function frameUrl(index) {
    const num = String(index + 1).padStart(CONFIG.frameDigits, '0');
    const useWebP = CONFIG.enableWebP && supportsWebP();
    const dir = useWebP ? CONFIG.webpDir : CONFIG.frameDir;
    const ext = useWebP ? '.webp' : '.jpg';
    return `${dir}/${CONFIG.framePrefix}${num}${ext}`;
  }

  // ── Progress bar (#17) ──
  function createProgressBar() {
    const bar = document.createElement('div');
    bar.id = 'frame-progress';
    bar.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      width: 0%;
      background: linear-gradient(90deg, #00d4aa, #4a9eff);
      z-index: 200;
      transition: width 0.15s ease-out, opacity 0.5s;
      box-shadow: 0 0 8px rgba(0,212,170,0.5);
      opacity: 1;
    `;
    document.body.appendChild(bar);
    return bar;
  }

  function updateProgress(pct) {
    if (!progressBar) return;
    progressBar.style.width = `${pct}%`;
    if (pct >= 100) {
      setTimeout(() => {
        progressBar.style.opacity = '0';
      }, 800);
    }
  }

  // ── Lazy-loading with IntersectionObserver (#11) ──
  function preloadFrames() {
    progressBar = createProgressBar();

    for (let i = 0; i < CONFIG.totalFrames; i++) {
      const img = new Image();
      images.push(img);
    }

    // Start loading immediately (low-priority batch)
    let batchIndex = 0;
    const batchSize = 10;

    function loadBatch() {
      const end = Math.min(batchIndex + batchSize, CONFIG.totalFrames);
      for (let i = batchIndex; i < end; i++) {
        images[i].src = frameUrl(i);
        images[i].addEventListener('load', () => {
          loaded++;
          updateProgress((loaded / CONFIG.totalFrames) * 100);
          if (loaded === 1) {
            resizeCanvas();
            drawFrame(0);
          }
          if (loaded === CONFIG.totalFrames) {
            console.log(`[ScrollFrames] All ${CONFIG.totalFrames} frames loaded`);
          }
        });
        images[i].addEventListener('error', () => {
          // Fallback: if WebP fails, try PNG
          if (CONFIG.enableWebP && images[i].src.includes('.webp')) {
            const jpgUrl = images[i].src
              .replace(CONFIG.webpDir, CONFIG.frameDir)
              .replace('.webp', '.jpg');
            images[i].src = jpgUrl;
          }
        });
      }
      batchIndex = end;
      if (batchIndex < CONFIG.totalFrames) {
        requestIdleCallback ? requestIdleCallback(loadBatch) : setTimeout(loadBatch, 16);
      }
    }

    loadBatch();
  }

  // ── Canvas sizing with retina support (#19) ──
  function resizeCanvas() {
    if (!canvas) return;
    const dpr = CONFIG.enableRetina ? window.devicePixelRatio || 1 : 1;
    canvas.width = window.innerWidth * dpr;
    canvas.height = window.innerHeight * dpr;
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    drawFrame(currentFrame);
  }

  // ── Draw a specific frame ──
  function drawFrame(index) {
    if (!ctx || !images[index] || !images[index].complete || !images[index].naturalWidth) return;
    const img = images[index];
    const dpr = CONFIG.enableRetina ? window.devicePixelRatio || 1 : 1;
    const cw = canvas.width / dpr;
    const ch = canvas.height / dpr;

    // Cover-fit
    const canvasAspect = cw / ch;
    const imgAspect = img.naturalWidth / img.naturalHeight;
    let sx = 0,
      sy = 0,
      sw = img.naturalWidth,
      sh = img.naturalHeight;

    if (imgAspect > canvasAspect) {
      sw = img.naturalHeight * canvasAspect;
      sx = (img.naturalWidth - sw) / 2;
    } else {
      sh = img.naturalWidth / canvasAspect;
      sy = (img.naturalHeight - sh) / 2;
    }

    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.drawImage(img, sx, sy, sw, sh, 0, 0, canvas.width, canvas.height);
    ctx.restore();
  }

  // ── Scroll handler ──
  function onScroll() {
    const container = document.querySelector('.scroll-video-container');
    if (!container) return;

    const rect = container.getBoundingClientRect();
    // Use the full scrollable height minus the viewport
    const containerHeight = container.scrollHeight - window.innerHeight;
    const scrolled = Math.max(0, -rect.top);
    const progress = containerHeight > 0 ? Math.max(0, Math.min(1, scrolled / containerHeight)) : 0;

    const targetFrame = Math.min(
      CONFIG.totalFrames - 1,
      Math.floor(progress * (CONFIG.totalFrames - 1)),
    );

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
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' },
    );

    document.querySelectorAll('.fade-in').forEach((el) => observer.observe(el));
  }

  // ── Register Service Worker (#8) ──
  function registerSW() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => console.log('[SW] Registered:', reg.scope))
        .catch((err) => console.warn('[SW] Registration failed:', err));
    }
  }

  // ── Init ──
  function init() {
    registerSW();

    if (!canvas || !ctx) {
      console.warn('[ScrollFrames] Canvas not found');
      return;
    }

    // A/B test: video fallback for low-power devices (#21)
    if (shouldUseVideoFallback()) {
      useVideoFallback = createVideoFallback();
      if (useVideoFallback) {
        initFadeAnimations();
        return; // Skip frame loading
      }
    }

    preloadFrames();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', resizeCanvas);
    initFadeAnimations();

    // Force an immediate scroll position check to draw the correct frame
    // if the page was loaded mid-scroll (e.g. browser back/forward)
    requestAnimationFrame(() => onScroll());

    console.log('[ScrollFrames] Controller v2 initialized');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

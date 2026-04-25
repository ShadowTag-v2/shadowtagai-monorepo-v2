/**
 * scroll-engine.js — Frame Sequence Controller
 *
 * Renders video frames on a <canvas> element driven by scroll position.
 * This is the core of the cinematic scroll effect.
 *
 * Usage:
 *   import { ScrollEngine } from './scroll-engine.js';
 *   const engine = new ScrollEngine({
 *     canvas: document.getElementById('hero-canvas'),
 *     container: document.getElementById('hero-section'),
 *     frameCount: 120,
 *     framePath: '/frames/frame_',
 *     frameExtension: '.png',
 *     preloadCount: 10,
 *   });
 *   engine.init();
 */

export class ScrollEngine {
  /**
   * @param {Object} config
   * @param {HTMLCanvasElement} config.canvas - Target canvas element
   * @param {HTMLElement} config.container - Scrollable container (sets scroll height)
   * @param {number} config.frameCount - Total number of frames
   * @param {string} config.framePath - Path prefix for frame images
   * @param {string} [config.frameExtension='.png'] - Frame file extension
   * @param {number} [config.preloadCount=10] - Frames to eagerly preload
   * @param {number} [config.bufferSize=5] - Frames to preload ahead of current
   * @param {function} [config.onFirstFrame] - Callback when first frame is loaded
   * @param {boolean} [config.preferWebP=true] - Use WebP if supported
   */
  constructor(config) {
    this.canvas = config.canvas;
    this.ctx = this.canvas.getContext('2d');
    this.container = config.container;
    this.frameCount = config.frameCount;
    this.framePath = config.framePath;
    this.frameExtension = config.frameExtension || '.png';
    this.preloadCount = config.preloadCount || 10;
    this.bufferSize = config.bufferSize || 5;
    this.onFirstFrame = config.onFirstFrame || null;
    this.preferWebP = config.preferWebP !== false;

    this.frames = new Array(this.frameCount);
    this.loadedFrames = new Set();
    this.currentFrame = 0;
    this.rafId = null;
    this.isReducedMotion = false;
    this._webpSupported = null;
  }

  /**
   * Detect WebP support.
   * @returns {Promise<boolean>}
   */
  async detectWebPSupport() {
    if (this._webpSupported !== null) return this._webpSupported;
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        this._webpSupported = img.width > 0 && img.height > 0;
        if (this._webpSupported && this.preferWebP) {
          this.frameExtension = '.webp';
        }
        resolve(this._webpSupported);
      };
      img.onerror = () => {
        this._webpSupported = false;
        resolve(false);
      };
      img.src = 'data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA';
    });
  }

  /**
   * Initialize the engine: resize canvas, preload frames, bind events.
   */
  async init() {
    // Respect prefers-reduced-motion
    this.isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Detect WebP support for smaller payloads
    await this.detectWebPSupport();

    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
    window.addEventListener('scroll', () => this.onScroll(), { passive: true });

    // Preload initial frames eagerly
    const preloadPromises = [];
    for (let i = 0; i < Math.min(this.preloadCount, this.frameCount); i++) {
      preloadPromises.push(this.loadFrame(i));
    }
    await Promise.all(preloadPromises);

    // Draw first frame and signal loading complete
    this.drawFrame(0);
    if (this.onFirstFrame) this.onFirstFrame();

    // If reduced motion, just show first frame and skip scroll binding
    if (this.isReducedMotion) {
      return;
    }

    // Start lazy loading remaining frames
    this.lazyLoadRemaining();
  }

  /**
   * Resize the canvas to match container width while maintaining aspect ratio.
   */
  resizeCanvas() {
    const dpr = window.devicePixelRatio || 1;
    const rect = this.container.getBoundingClientRect();
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.canvas.style.width = `${rect.width}px`;
    this.canvas.style.height = `${rect.height}px`;
    this.ctx.scale(dpr, dpr);

    // Redraw current frame at new size
    if (this.frames[this.currentFrame]) {
      this.drawFrame(this.currentFrame);
    }
  }

  /**
   * Load a single frame image.
   * @param {number} index - Frame index (0-based)
   * @returns {Promise<HTMLImageElement>}
   */
  loadFrame(index) {
    if (this.frames[index]) {
      return Promise.resolve(this.frames[index]);
    }

    return new Promise((resolve, reject) => {
      const img = new Image();
      const paddedIndex = String(index + 1).padStart(4, '0');
      img.src = `${this.framePath}${paddedIndex}${this.frameExtension}`;

      img.onload = () => {
        this.frames[index] = img;
        this.loadedFrames.add(index);
        resolve(img);
      };

      img.onerror = () => {
        reject(new Error(`Frame ${index} failed to load`));
      };
    });
  }

  /**
   * Draw a specific frame on the canvas.
   * @param {number} index - Frame index
   */
  drawFrame(index) {
    const img = this.frames[index];
    if (!img) return;

    const canvasWidth = this.canvas.width / (window.devicePixelRatio || 1);
    const canvasHeight = this.canvas.height / (window.devicePixelRatio || 1);

    // Cover-fit the image (like CSS object-fit: cover)
    const imgRatio = img.width / img.height;
    const canvasRatio = canvasWidth / canvasHeight;

    let drawWidth, drawHeight, drawX, drawY;

    if (imgRatio > canvasRatio) {
      drawHeight = canvasHeight;
      drawWidth = canvasHeight * imgRatio;
      drawX = (canvasWidth - drawWidth) / 2;
      drawY = 0;
    } else {
      drawWidth = canvasWidth;
      drawHeight = canvasWidth / imgRatio;
      drawX = 0;
      drawY = (canvasHeight - drawHeight) / 2;
    }

    this.ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    this.ctx.drawImage(img, drawX, drawY, drawWidth, drawHeight);
  }

  /**
   * Handle scroll event — compute which frame to show.
   */
  onScroll() {
    if (this.isReducedMotion) return;

    if (this.rafId) return; // Debounce via rAF

    this.rafId = requestAnimationFrame(() => {
      this.rafId = null;

      const containerRect = this.container.getBoundingClientRect();
      const containerTop = containerRect.top + window.scrollY;
      const scrollableHeight = containerRect.height - window.innerHeight;

      if (scrollableHeight <= 0) return;

      const scrollProgress = Math.max(
        0,
        Math.min(1, (window.scrollY - containerTop) / scrollableHeight),
      );

      const targetFrame = Math.min(
        Math.floor(scrollProgress * this.frameCount),
        this.frameCount - 1,
      );

      if (targetFrame !== this.currentFrame) {
        this.currentFrame = targetFrame;
        this.drawFrame(targetFrame);

        // Preload ahead
        this.preloadAhead(targetFrame);
      }
    });
  }

  /**
   * Preload frames ahead of the current position.
   * @param {number} currentIndex - Current frame index
   */
  preloadAhead(currentIndex) {
    for (let i = 1; i <= this.bufferSize; i++) {
      const nextIndex = currentIndex + i;
      if (nextIndex < this.frameCount && !this.loadedFrames.has(nextIndex)) {
        this.loadFrame(nextIndex).catch(() => {
          /* frame load errors are non-fatal */
        });
      }
    }
  }

  /**
   * Lazy-load remaining frames in the background using IntersectionObserver-like batching.
   */
  lazyLoadRemaining() {
    const batchSize = 5;
    let startIndex = this.preloadCount;

    const loadBatch = () => {
      if (startIndex >= this.frameCount) return;

      const endIndex = Math.min(startIndex + batchSize, this.frameCount);
      const promises = [];

      for (let i = startIndex; i < endIndex; i++) {
        if (!this.loadedFrames.has(i)) {
          promises.push(
            this.loadFrame(i).catch(() => {
              /* non-fatal */
            }),
          );
        }
      }

      startIndex = endIndex;

      // Use requestIdleCallback for non-blocking loading
      if ('requestIdleCallback' in window) {
        Promise.all(promises).then(() => {
          requestIdleCallback(() => loadBatch());
        });
      } else {
        Promise.all(promises).then(() => {
          setTimeout(() => loadBatch(), 100);
        });
      }
    };

    // Start background loading after initial render
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => loadBatch());
    } else {
      setTimeout(() => loadBatch(), 500);
    }
  }

  /**
   * Destroy the engine, removing event listeners.
   */
  destroy() {
    window.removeEventListener('resize', this.resizeCanvas);
    window.removeEventListener('scroll', this.onScroll);
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
    }
    this.frames = [];
    this.loadedFrames.clear();
  }
}

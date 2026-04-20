/**
 * Scroll Animation Controller
 *
 * Plays through a sequence of extracted video frames based on scroll position.
 * Creates Apple-style cinematic scroll effects without choppy <video> playback.
 *
 * Usage:
 *   <canvas id="scroll-canvas" width="1280" height="720"></canvas>
 *   <script src="scroll-animation.js"></script>
 *   <script>
 *     ScrollAnimator.init({
 *       canvasId: 'scroll-canvas',
 *       frameDir: '/frames/hero_drift',
 *       framePrefix: 'frame_',
 *       frameExtension: '.png',
 *       totalFrames: 240,
 *       scrollHeight: 3000,
 *     });
 *   </script>
 */

const ScrollAnimator = (() => {
  let canvas = null;
  let ctx = null;
  let frames = [];
  let currentFrame = -1;
  let totalFrames = 0;
  let scrollHeight = 0;
  let isLoaded = false;
  let loadedCount = 0;
  let rafId = null;

  /**
   * Initialize the scroll animation controller.
   * @param {Object} config - Configuration object.
   * @param {string} config.canvasId - ID of the target canvas element.
   * @param {string} config.frameDir - Directory containing frame images.
   * @param {string} [config.framePrefix='frame_'] - Frame filename prefix.
   * @param {string} [config.frameExtension='.png'] - Frame file extension.
   * @param {number} config.totalFrames - Total number of frames.
   * @param {number} [config.scrollHeight=3000] - Virtual scroll height in pixels.
   * @param {Function} [config.onProgress] - Loading progress callback (0-1).
   * @param {Function} [config.onReady] - Called when all frames are loaded.
   */
  function init(config) {
    canvas = document.getElementById(config.canvasId);
    if (!canvas) {
      console.error(`[ScrollAnimator] Canvas #${config.canvasId} not found.`);
      return;
    }

    ctx = canvas.getContext('2d');
    totalFrames = config.totalFrames;
    scrollHeight = config.scrollHeight || 3000;

    const frameDir = config.frameDir.replace(/\/$/, '');
    const prefix = config.framePrefix || 'frame_';
    const ext = config.frameExtension || '.png';
    const onProgress = config.onProgress || (() => {});
    const onReady = config.onReady || (() => {});

    // Set scroll container height
    const container = canvas.closest('[data-scroll-container]') || document.body;
    container.style.height = `${scrollHeight + window.innerHeight}px`;

    // Preload all frames
    frames = new Array(totalFrames);
    loadedCount = 0;

    for (let i = 0; i < totalFrames; i++) {
      const img = new Image();
      const padded = String(i + 1).padStart(4, '0');
      img.src = `${frameDir}/${prefix}${padded}${ext}`;

      img.onload = () => {
        loadedCount++;
        onProgress(loadedCount / totalFrames);
        if (loadedCount === totalFrames) {
          isLoaded = true;
          onReady();
          render();
        }
      };

      img.onerror = () => {
        console.warn(`[ScrollAnimator] Failed to load: ${img.src}`);
        loadedCount++;
        if (loadedCount === totalFrames) {
          isLoaded = true;
          onReady();
          render();
        }
      };

      frames[i] = img;
    }

    // Bind scroll listener with RAF throttle
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onResize, { passive: true });

    // Initial canvas sizing
    onResize();
  }

  function onScroll() {
    if (rafId) return;
    rafId = requestAnimationFrame(() => {
      render();
      rafId = null;
    });
  }

  function onResize() {
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * (window.devicePixelRatio || 1);
    canvas.height = rect.height * (window.devicePixelRatio || 1);
    ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);
    render();
  }

  function render() {
    if (!isLoaded || !ctx || totalFrames === 0) return;

    const maxScroll = scrollHeight;
    const scrollTop = window.scrollY || window.pageYOffset;
    const scrollFraction = Math.min(Math.max(scrollTop / maxScroll, 0), 1);
    const frameIndex = Math.min(Math.floor(scrollFraction * totalFrames), totalFrames - 1);

    if (frameIndex === currentFrame) return;
    currentFrame = frameIndex;

    const img = frames[frameIndex];
    if (!img || !img.complete || !img.naturalWidth) return;

    // Cover-fit the frame to the canvas
    const canvasW = canvas.width / (window.devicePixelRatio || 1);
    const canvasH = canvas.height / (window.devicePixelRatio || 1);
    const imgRatio = img.naturalWidth / img.naturalHeight;
    const canvasRatio = canvasW / canvasH;

    let drawW, drawH, drawX, drawY;
    if (imgRatio > canvasRatio) {
      drawH = canvasH;
      drawW = canvasH * imgRatio;
      drawX = (canvasW - drawW) / 2;
      drawY = 0;
    } else {
      drawW = canvasW;
      drawH = canvasW / imgRatio;
      drawX = 0;
      drawY = (canvasH - drawH) / 2;
    }

    ctx.clearRect(0, 0, canvasW, canvasH);
    ctx.drawImage(img, drawX, drawY, drawW, drawH);
  }

  /**
   * Destroy the scroll animator and clean up resources.
   */
  function destroy() {
    window.removeEventListener('scroll', onScroll);
    window.removeEventListener('resize', onResize);
    if (rafId) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    frames = [];
    currentFrame = -1;
    isLoaded = false;
  }

  /**
   * Get the current loading progress.
   * @returns {number} Progress from 0 to 1.
   */
  function getProgress() {
    return totalFrames > 0 ? loadedCount / totalFrames : 0;
  }

  return { init, destroy, getProgress };
})();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ScrollAnimator;
}

/**
 * Mobile Performance Optimization Utilities
 * Enhances performance for mobile devices
 */

const MobilePerformance = {
  /**
   * Debounce function for performance-critical events
   */
  debounce(func, wait = 250) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  /**
   * Throttle function for scroll and resize events
   */
  throttle(func, limit = 100) {
    let inThrottle;
    return function executedFunction(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  /**
   * Request Animation Frame wrapper for smooth animations
   */
  raf(callback) {
    return window.requestAnimationFrame(callback);
  },

  /**
   * Cancel Animation Frame
   */
  cancelRaf(id) {
    return window.cancelAnimationFrame(id);
  },

  /**
   * Lazy load images
   */
  lazyLoadImages(selector = 'img[data-src]') {
    const images = document.querySelectorAll(selector);

    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            observer.unobserve(img);

            img.addEventListener('load', () => {
              img.classList.add('loaded');
            });
          }
        });
      }, {
        rootMargin: '50px 0px',
        threshold: 0.01
      });

      images.forEach(img => imageObserver.observe(img));
    } else {
      // Fallback for browsers without IntersectionObserver
      images.forEach(img => {
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
      });
    }
  },

  /**
   * Detect if user is on mobile device
   */
  isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  },

  /**
   * Detect if device supports touch
   */
  hasTouch() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  },

  /**
   * Get device pixel ratio for responsive images
   */
  getPixelRatio() {
    return window.devicePixelRatio || 1;
  },

  /**
   * Detect network connection type
   */
  getConnectionType() {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    return connection ? {
      type: connection.effectiveType,
      downlink: connection.downlink,
      rtt: connection.rtt,
      saveData: connection.saveData
    } : null;
  },

  /**
   * Optimize for slow connections
   */
  isSlow Connection() {
    const connection = this.getConnectionType();
    if (!connection) return false;
    return connection.saveData || connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g';
  },

  /**
   * Reduce motion preference detection
   */
  prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  },

  /**
   * Virtual scrolling for large lists
   */
  createVirtualScroller(container, items, itemHeight, renderItem) {
    const scrollContainer = container;
    const totalHeight = items.length * itemHeight;
    const viewportHeight = scrollContainer.clientHeight;
    const visibleItems = Math.ceil(viewportHeight / itemHeight) + 2;

    let scrollTop = 0;

    const render = () => {
      const startIndex = Math.floor(scrollTop / itemHeight);
      const endIndex = Math.min(startIndex + visibleItems, items.length);

      scrollContainer.innerHTML = '';
      scrollContainer.style.height = `${totalHeight}px`;
      scrollContainer.style.position = 'relative';

      for (let i = startIndex; i < endIndex; i++) {
        const item = renderItem(items[i], i);
        item.style.position = 'absolute';
        item.style.top = `${i * itemHeight}px`;
        item.style.height = `${itemHeight}px`;
        scrollContainer.appendChild(item);
      }
    };

    scrollContainer.addEventListener('scroll', this.throttle(() => {
      scrollTop = scrollContainer.scrollTop;
      render();
    }, 16));

    render();
  },

  /**
   * Optimize scroll performance
   */
  optimizeScroll(callback) {
    let ticking = false;

    const update = () => {
      callback();
      ticking = false;
    };

    return () => {
      if (!ticking) {
        window.requestAnimationFrame(update);
        ticking = true;
      }
    };
  },

  /**
   * Preload critical resources
   */
  preloadResource(url, type = 'script') {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = url;
    link.as = type;
    document.head.appendChild(link);
  },

  /**
   * Defer non-critical resources
   */
  deferResource(url, type = 'script') {
    return new Promise((resolve, reject) => {
      if (type === 'script') {
        const script = document.createElement('script');
        script.src = url;
        script.defer = true;
        script.onload = resolve;
        script.onerror = reject;
        document.body.appendChild(script);
      } else if (type === 'style') {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = url;
        link.onload = resolve;
        link.onerror = reject;
        document.head.appendChild(link);
      }
    });
  },

  /**
   * Memory-efficient event delegation
   */
  delegate(element, eventType, selector, handler) {
    element.addEventListener(eventType, (event) => {
      const target = event.target.closest(selector);
      if (target && element.contains(target)) {
        handler.call(target, event);
      }
    });
  },

  /**
   * Battery status detection
   */
  async getBatteryStatus() {
    if ('getBattery' in navigator) {
      try {
        const battery = await navigator.getBattery();
        return {
          level: battery.level,
          charging: battery.charging,
          chargingTime: battery.chargingTime,
          dischargingTime: battery.dischargingTime
        };
      } catch (error) {
        console.warn('Battery API not available:', error);
        return null;
      }
    }
    return null;
  },

  /**
   * Adaptive loading based on device capabilities
   */
  async shouldLoadHeavyAssets() {
    const battery = await this.getBatteryStatus();
    const connection = this.getConnectionType();

    // Don't load heavy assets if battery is low or connection is slow
    if (battery && battery.level < 0.2 && !battery.charging) {
      return false;
    }

    if (connection && (connection.saveData || this.isSlowConnection())) {
      return false;
    }

    return true;
  },

  /**
   * Web vitals monitoring
   */
  measurePerformance() {
    if ('PerformanceObserver' in window) {
      // Largest Contentful Paint (LCP)
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime);
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      } catch (e) {
        console.warn('LCP observer failed:', e);
      }

      // First Input Delay (FID)
      try {
        const fidObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach(entry => {
            console.log('FID:', entry.processingStart - entry.startTime);
          });
        });
        fidObserver.observe({ entryTypes: ['first-input'] });
      } catch (e) {
        console.warn('FID observer failed:', e);
      }

      // Cumulative Layout Shift (CLS)
      try {
        let clsScore = 0;
        const clsObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              clsScore += entry.value;
            }
          }
          console.log('CLS:', clsScore);
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });
      } catch (e) {
        console.warn('CLS observer failed:', e);
      }
    }

    // Navigation timing
    window.addEventListener('load', () => {
      setTimeout(() => {
        const perfData = performance.getEntriesByType('navigation')[0];
        if (perfData) {
          console.log('Page Load Metrics:', {
            dns: perfData.domainLookupEnd - perfData.domainLookupStart,
            tcp: perfData.connectEnd - perfData.connectStart,
            ttfb: perfData.responseStart - perfData.requestStart,
            download: perfData.responseEnd - perfData.responseStart,
            domInteractive: perfData.domInteractive,
            domComplete: perfData.domComplete,
            loadComplete: perfData.loadEventEnd
          });
        }
      }, 0);
    });
  },

  /**
   * Initialize all performance optimizations
   */
  init(options = {}) {
    console.log('[Mobile Performance] Initializing...');

    // Lazy load images
    if (options.lazyLoadImages !== false) {
      this.lazyLoadImages();
    }

    // Measure performance
    if (options.measurePerformance !== false) {
      this.measurePerformance();
    }

    // Log device info
    console.log('[Mobile Performance] Device Info:', {
      isMobile: this.isMobile(),
      hasTouch: this.hasTouch(),
      pixelRatio: this.getPixelRatio(),
      connection: this.getConnectionType(),
      reducedMotion: this.prefersReducedMotion()
    });
  }
};

// Auto-initialize on load
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    MobilePerformance.init();
  });
} else {
  MobilePerformance.init();
}

// Export for use in modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = MobilePerformance;
}

/**
 * Main Application Entry Point
 * Initializes PWA features and mobile optimizations
 */

class MobileApp {
  constructor() {
    this.isOnline = navigator.onLine;
    this.isInstalled = false;
    this.deferredPrompt = null;

    this.init();
  }

  async init() {
    console.log('[MobileApp] Initializing...');

    // Register service worker
    await this.registerServiceWorker();

    // Setup PWA install prompt
    this.setupInstallPrompt();

    // Setup touch gestures
    this.setupGestures();

    // Setup network monitoring
    this.setupNetworkMonitoring();

    // Setup UI event listeners
    this.setupEventListeners();

    console.log('[MobileApp] Initialization complete');
  }

  async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js', {
          scope: '/',
        });

        console.log('[ServiceWorker] Registered successfully:', registration.scope);

        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          console.log('[ServiceWorker] Update found');

          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              this.showUpdateNotification();
            }
          });
        });

        // Listen for messages from service worker
        navigator.serviceWorker.addEventListener('message', (event) => {
          console.log('[ServiceWorker] Message received:', event.data);
        });
      } catch (error) {
        console.error('[ServiceWorker] Registration failed:', error);
      }
    }
  }

  setupInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (e) => {
      console.log('[PWA] Install prompt available');
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallButton();
    });

    window.addEventListener('appinstalled', () => {
      console.log('[PWA] App installed');
      this.isInstalled = true;
      this.hideInstallButton();
    });

    // Check if already installed
    if (
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true
    ) {
      this.isInstalled = true;
      console.log('[PWA] Running as installed app');
    }
  }

  async promptInstall() {
    if (!this.deferredPrompt) {
      console.log('[PWA] Install prompt not available');
      return;
    }

    this.deferredPrompt.prompt();
    const { outcome } = await this.deferredPrompt.userChoice;
    console.log('[PWA] Install prompt outcome:', outcome);

    this.deferredPrompt = null;
    this.hideInstallButton();
  }

  showInstallButton() {
    const installBtn = document.getElementById('install-button');
    if (installBtn) {
      installBtn.style.display = 'block';
      installBtn.addEventListener('click', () => this.promptInstall());
    }
  }

  hideInstallButton() {
    const installBtn = document.getElementById('install-button');
    if (installBtn) {
      installBtn.style.display = 'none';
    }
  }

  setupGestures() {
    const appContainer = document.getElementById('app-container');
    if (!appContainer) return;

    // Initialize touch gestures
    const gestures = new TouchGestureHandler(appContainer, {
      threshold: 75,
      preventScroll: false,
    });

    // Listen for swipe events
    appContainer.addEventListener('swipeleft', (e) => {
      console.log('[Gesture] Swipe left', e.detail);
      this.handleSwipeLeft();
    });

    appContainer.addEventListener('swiperight', (e) => {
      console.log('[Gesture] Swipe right', e.detail);
      this.handleSwipeRight();
    });

    appContainer.addEventListener('tap', (e) => {
      console.log('[Gesture] Tap', e.detail);
    });

    // Pull to refresh
    const pullToRefresh = new PullToRefreshHandler(appContainer, () => this.refreshContent());

    appContainer.addEventListener('pullmove', (e) => {
      this.showRefreshIndicator(e.detail.distance);
    });

    appContainer.addEventListener('refreshstart', () => {
      this.showRefreshLoader();
    });

    appContainer.addEventListener('refreshend', (e) => {
      this.hideRefreshLoader();
      if (e.detail.success) {
        this.showMessage('Content refreshed!');
      }
    });
  }

  setupNetworkMonitoring() {
    window.addEventListener('online', () => {
      console.log('[Network] Online');
      this.isOnline = true;
      this.updateOnlineStatus();
      this.showMessage('Back online!', 'success');
    });

    window.addEventListener('offline', () => {
      console.log('[Network] Offline');
      this.isOnline = false;
      this.updateOnlineStatus();
      this.showMessage('You are offline', 'warning');
    });

    // Monitor connection changes
    if ('connection' in navigator) {
      navigator.connection.addEventListener('change', () => {
        const connection = MobilePerformance.getConnectionType();
        console.log('[Network] Connection changed:', connection);
      });
    }
  }

  updateOnlineStatus() {
    const statusEl = document.getElementById('online-status');
    if (statusEl) {
      statusEl.textContent = this.isOnline ? 'Online' : 'Offline';
      statusEl.className = this.isOnline ? 'status-online' : 'status-offline';
    }
  }

  setupEventListeners() {
    // Prevent default touch behaviors that might interfere
    document.addEventListener(
      'touchmove',
      (e) => {
        if (e.scale && e.scale !== 1) {
          e.preventDefault();
        }
      },
      { passive: false },
    );

    // Handle visibility changes for performance
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        console.log('[App] Page hidden');
      } else {
        console.log('[App] Page visible');
        this.checkForUpdates();
      }
    });

    // Handle orientation changes
    window.addEventListener('orientationchange', () => {
      console.log('[Device] Orientation changed:', window.orientation);
      this.handleOrientationChange();
    });
  }

  handleSwipeLeft() {
    // Implement navigation or action for swipe left
    console.log('[App] Handle swipe left');
  }

  handleSwipeRight() {
    // Implement navigation or action for swipe right
    console.log('[App] Handle swipe right');
  }

  async refreshContent() {
    console.log('[App] Refreshing content...');
    // Implement content refresh logic
    return new Promise((resolve) => {
      setTimeout(() => {
        console.log('[App] Content refreshed');
        resolve();
      }, 1000);
    });
  }

  showRefreshIndicator(distance) {
    const indicator = document.getElementById('refresh-indicator');
    if (indicator) {
      const progress = Math.min(distance / 80, 1);
      indicator.style.opacity = progress;
      indicator.style.transform = `translateY(${distance}px) rotate(${progress * 360}deg)`;
    }
  }

  showRefreshLoader() {
    const loader = document.getElementById('refresh-loader');
    if (loader) {
      loader.style.display = 'block';
    }
  }

  hideRefreshLoader() {
    const loader = document.getElementById('refresh-loader');
    if (loader) {
      loader.style.display = 'none';
    }
    const indicator = document.getElementById('refresh-indicator');
    if (indicator) {
      indicator.style.opacity = 0;
      indicator.style.transform = 'translateY(0) rotate(0)';
    }
  }

  showMessage(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('show');
    }, 10);

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  showUpdateNotification() {
    this.showMessage('A new version is available. Refresh to update.', 'info');
  }

  async checkForUpdates() {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      const registration = await navigator.serviceWorker.getRegistration();
      if (registration) {
        registration.update();
      }
    }
  }

  handleOrientationChange() {
    // Handle UI adjustments for orientation changes
    const isPortrait = window.matchMedia('(orientation: portrait)').matches;
    console.log('[App] Orientation is', isPortrait ? 'portrait' : 'landscape');
  }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.mobileApp = new MobileApp();
  });
} else {
  window.mobileApp = new MobileApp();
}

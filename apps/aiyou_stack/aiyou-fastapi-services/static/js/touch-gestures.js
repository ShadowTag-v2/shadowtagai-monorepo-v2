/**
 * Touch Gesture Handler
 * Provides native-like touch interactions for mobile web apps
 */

class TouchGestureHandler {
  constructor(element, options = {}) {
    this.element = element;
    this.options = {
      threshold: options.threshold || 50,
      velocity: options.velocity || 0.3,
      allowedTime: options.allowedTime || 300,
      preventScroll: options.preventScroll || false,
      ...options,
    };

    this.startX = 0;
    this.startY = 0;
    this.startTime = 0;
    this.distX = 0;
    this.distY = 0;
    this.isSwiping = false;

    this.init();
  }

  init() {
    // Touch events
    this.element.addEventListener("touchstart", this.handleTouchStart.bind(this), {
      passive: !this.options.preventScroll,
    });
    this.element.addEventListener("touchmove", this.handleTouchMove.bind(this), {
      passive: !this.options.preventScroll,
    });
    this.element.addEventListener("touchend", this.handleTouchEnd.bind(this), { passive: true });
    this.element.addEventListener("touchcancel", this.handleTouchCancel.bind(this), {
      passive: true,
    });

    // Pointer events for broader device support
    if (window.PointerEvent) {
      this.element.addEventListener("pointerdown", this.handlePointerDown.bind(this));
      this.element.addEventListener("pointermove", this.handlePointerMove.bind(this));
      this.element.addEventListener("pointerup", this.handlePointerUp.bind(this));
      this.element.addEventListener("pointercancel", this.handlePointerCancel.bind(this));
    }
  }

  handleTouchStart(e) {
    const touch = e.touches[0];
    this.startX = touch.pageX;
    this.startY = touch.pageY;
    this.startTime = Date.now();
    this.isSwiping = true;

    this.dispatchCustomEvent("gesturestart", { x: this.startX, y: this.startY });
  }

  handleTouchMove(e) {
    if (!this.isSwiping) return;

    const touch = e.touches[0];
    this.distX = touch.pageX - this.startX;
    this.distY = touch.pageY - this.startY;

    if (this.options.preventScroll && Math.abs(this.distX) > Math.abs(this.distY)) {
      e.preventDefault();
    }

    this.dispatchCustomEvent("gesturemove", {
      x: touch.pageX,
      y: touch.pageY,
      distX: this.distX,
      distY: this.distY,
    });
  }

  handleTouchEnd(e) {
    if (!this.isSwiping) return;

    const elapsedTime = Date.now() - this.startTime;

    // Determine gesture type
    if (elapsedTime <= this.options.allowedTime) {
      const velocity = Math.abs(this.distX) / elapsedTime;

      if (Math.abs(this.distX) >= this.options.threshold && velocity >= this.options.velocity) {
        // Horizontal swipe
        const direction = this.distX > 0 ? "right" : "left";
        this.dispatchCustomEvent("swipe", { direction, distance: this.distX, velocity });
        this.dispatchCustomEvent(`swipe${direction}`, { distance: this.distX, velocity });
      } else if (Math.abs(this.distY) >= this.options.threshold) {
        // Vertical swipe
        const direction = this.distY > 0 ? "down" : "up";
        this.dispatchCustomEvent("swipe", { direction, distance: this.distY, velocity });
        this.dispatchCustomEvent(`swipe${direction}`, { distance: this.distY, velocity });
      } else {
        // Tap
        this.dispatchCustomEvent("tap", { x: this.startX, y: this.startY });
      }
    } else {
      // Long press
      this.dispatchCustomEvent("longpress", {
        x: this.startX,
        y: this.startY,
        duration: elapsedTime,
      });
    }

    this.dispatchCustomEvent("gestureend", {
      distX: this.distX,
      distY: this.distY,
      duration: elapsedTime,
    });

    this.reset();
  }

  handleTouchCancel(e) {
    this.reset();
  }

  // Pointer event handlers for mouse/pen support
  handlePointerDown(e) {
    this.startX = e.pageX;
    this.startY = e.pageY;
    this.startTime = Date.now();
    this.isSwiping = true;
  }

  handlePointerMove(e) {
    if (!this.isSwiping) return;
    this.distX = e.pageX - this.startX;
    this.distY = e.pageY - this.startY;
  }

  handlePointerUp(e) {
    this.handleTouchEnd(e);
  }

  handlePointerCancel(e) {
    this.reset();
  }

  dispatchCustomEvent(eventName, detail) {
    const event = new CustomEvent(eventName, {
      detail,
      bubbles: true,
      cancelable: true,
    });
    this.element.dispatchEvent(event);
  }

  reset() {
    this.startX = 0;
    this.startY = 0;
    this.startTime = 0;
    this.distX = 0;
    this.distY = 0;
    this.isSwiping = false;
  }

  destroy() {
    this.element.removeEventListener("touchstart", this.handleTouchStart);
    this.element.removeEventListener("touchmove", this.handleTouchMove);
    this.element.removeEventListener("touchend", this.handleTouchEnd);
    this.element.removeEventListener("touchcancel", this.handleTouchCancel);

    if (window.PointerEvent) {
      this.element.removeEventListener("pointerdown", this.handlePointerDown);
      this.element.removeEventListener("pointermove", this.handlePointerMove);
      this.element.removeEventListener("pointerup", this.handlePointerUp);
      this.element.removeEventListener("pointercancel", this.handlePointerCancel);
    }
  }
}

/**
 * Pinch-to-Zoom Gesture Handler
 */
class PinchZoomHandler {
  constructor(element, options = {}) {
    this.element = element;
    this.options = {
      minScale: options.minScale || 0.5,
      maxScale: options.maxScale || 3,
      ...options,
    };

    this.scale = 1;
    this.initialDistance = 0;
    this.isPinching = false;

    this.init();
  }

  init() {
    this.element.addEventListener("touchstart", this.handleTouchStart.bind(this), {
      passive: true,
    });
    this.element.addEventListener("touchmove", this.handleTouchMove.bind(this), { passive: false });
    this.element.addEventListener("touchend", this.handleTouchEnd.bind(this), { passive: true });
  }

  handleTouchStart(e) {
    if (e.touches.length === 2) {
      this.isPinching = true;
      this.initialDistance = this.getDistance(e.touches[0], e.touches[1]);
    }
  }

  handleTouchMove(e) {
    if (!this.isPinching || e.touches.length !== 2) return;

    e.preventDefault();

    const currentDistance = this.getDistance(e.touches[0], e.touches[1]);
    const scaleChange = currentDistance / this.initialDistance;
    const newScale = Math.max(
      this.options.minScale,
      Math.min(this.options.maxScale, this.scale * scaleChange),
    );

    this.dispatchCustomEvent("pinch", {
      scale: newScale,
      delta: scaleChange,
    });

    this.initialDistance = currentDistance;
  }

  handleTouchEnd(e) {
    if (e.touches.length < 2) {
      this.isPinching = false;
    }
  }

  getDistance(touch1, touch2) {
    const dx = touch2.pageX - touch1.pageX;
    const dy = touch2.pageY - touch1.pageY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  dispatchCustomEvent(eventName, detail) {
    const event = new CustomEvent(eventName, {
      detail,
      bubbles: true,
      cancelable: true,
    });
    this.element.dispatchEvent(event);
  }

  setScale(scale) {
    this.scale = Math.max(this.options.minScale, Math.min(this.options.maxScale, scale));
  }

  destroy() {
    this.element.removeEventListener("touchstart", this.handleTouchStart);
    this.element.removeEventListener("touchmove", this.handleTouchMove);
    this.element.removeEventListener("touchend", this.handleTouchEnd);
  }
}

/**
 * Pull-to-Refresh Handler
 */
class PullToRefreshHandler {
  constructor(element, onRefresh, options = {}) {
    this.element = element;
    this.onRefresh = onRefresh;
    this.options = {
      threshold: options.threshold || 80,
      maxPull: options.maxPull || 120,
      ...options,
    };

    this.startY = 0;
    this.currentY = 0;
    this.isPulling = false;
    this.isRefreshing = false;

    this.init();
  }

  init() {
    this.element.addEventListener("touchstart", this.handleTouchStart.bind(this), {
      passive: true,
    });
    this.element.addEventListener("touchmove", this.handleTouchMove.bind(this), { passive: false });
    this.element.addEventListener("touchend", this.handleTouchEnd.bind(this), { passive: true });
  }

  handleTouchStart(e) {
    if (this.element.scrollTop === 0) {
      this.startY = e.touches[0].pageY;
      this.isPulling = true;
    }
  }

  handleTouchMove(e) {
    if (!this.isPulling || this.isRefreshing) return;

    this.currentY = e.touches[0].pageY;
    const pullDistance = Math.min(this.currentY - this.startY, this.options.maxPull);

    if (pullDistance > 0) {
      e.preventDefault();
      this.dispatchCustomEvent("pullmove", { distance: pullDistance });
    }
  }

  async handleTouchEnd(e) {
    if (!this.isPulling || this.isRefreshing) return;

    const pullDistance = this.currentY - this.startY;

    if (pullDistance >= this.options.threshold) {
      this.isRefreshing = true;
      this.dispatchCustomEvent("refreshstart");

      try {
        await this.onRefresh();
        this.dispatchCustomEvent("refreshend", { success: true });
      } catch (error) {
        this.dispatchCustomEvent("refreshend", { success: false, error });
      } finally {
        this.isRefreshing = false;
      }
    }

    this.isPulling = false;
    this.startY = 0;
    this.currentY = 0;
  }

  dispatchCustomEvent(eventName, detail = {}) {
    const event = new CustomEvent(eventName, {
      detail,
      bubbles: true,
      cancelable: true,
    });
    this.element.dispatchEvent(event);
  }

  destroy() {
    this.element.removeEventListener("touchstart", this.handleTouchStart);
    this.element.removeEventListener("touchmove", this.handleTouchMove);
    this.element.removeEventListener("touchend", this.handleTouchEnd);
  }
}

// Export for use in modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    TouchGestureHandler,
    PinchZoomHandler,
    PullToRefreshHandler,
  };
}

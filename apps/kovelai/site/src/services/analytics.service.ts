/**
 * Analytics Service
 *
 * Client-side analytics abstraction. Currently a no-op shell
 * that will be wired to GA4 when NEXT_PUBLIC_GA_MEASUREMENT_ID is set.
 */

const GA_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID;

/**
 * Tracks a custom event to GA4.
 * No-ops gracefully if analytics is not configured.
 */
export function trackEvent(
  eventName: string,
  params?: Record<string, string | number | boolean>,
): void {
  if (typeof window === "undefined" || !GA_ID) return;

  // gtag is injected by the GA4 script tag in layout.tsx
  const gtag = (window as unknown as { gtag?: (...args: unknown[]) => void }).gtag;
  if (gtag) {
    gtag("event", eventName, params);
  }
}

/**
 * Tracks a page view. Called automatically by Next.js route changes
 * when GA4 is configured.
 */
export function trackPageView(url: string): void {
  trackEvent("page_view", { page_path: url });
}

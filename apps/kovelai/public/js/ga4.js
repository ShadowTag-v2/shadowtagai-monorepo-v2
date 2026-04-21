/**
 * GA4 Analytics + Conversion Tracking
 * Extracted from inline script for CSP compliance (no unsafe-inline needed).
 */

window.dataLayer = window.dataLayer || [];
function gtag() {
  dataLayer.push(arguments);
}
gtag('js', new Date());
gtag('config', 'G-5QW1DZL23V');

// Conversion tracking events
document.addEventListener('DOMContentLoaded', () => {
  var ctaEvents = {
    'cta-start': { event: 'generate_lead', plan: 'trial_nav' },
    'cta-solo': { event: 'begin_checkout', plan: 'solo_299' },
    'cta-practice': { event: 'begin_checkout', plan: 'practice_599' },
    'cta-enterprise': { event: 'contact_sales', plan: 'enterprise_999' },
  };
  Object.keys(ctaEvents).forEach((id) => {
    var el = document.getElementById(id);
    if (el)
      el.addEventListener('click', () => {
        gtag('event', ctaEvents[id].event, {
          event_category: 'engagement',
          event_label: ctaEvents[id].plan,
          value: 1,
        });
      });
  });
});

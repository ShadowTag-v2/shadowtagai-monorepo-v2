/**
 * Intersection Observer for fade-in animations.
 * Extracted for CSP compliance.
 */

document.addEventListener('DOMContentLoaded', () => {
  var observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.1 },
  );

  document.querySelectorAll('.fade-in').forEach((el) => {
    observer.observe(el);
  });

  // Register service worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(() => {});
  }
});

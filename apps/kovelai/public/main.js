/**
 * KovelAI — Main Application Script
 * Handles: nav, modals, intersection observer, smooth scroll, dynamic effects
 */

(function () {
  'use strict';

  // ── DOM References ──
  const nav = document.getElementById('main-nav');
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');
  const contactModal = document.getElementById('contactModal');

  // ── Nav Background on Scroll ──
  function handleNavScroll() {
    if (!nav) return;
    if (window.scrollY > 60) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  }
  window.addEventListener('scroll', handleNavScroll, { passive: true });
  handleNavScroll();

  // ── Mobile Nav Toggle ──
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      navLinks.classList.toggle('open');
      const isOpen = navLinks.classList.contains('open');
      navToggle.setAttribute('aria-expanded', isOpen);
      navToggle.textContent = isOpen ? '✕' : '☰';
    });

    // Close mobile nav when clicking a link
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        if (window.innerWidth <= 768) {
          navLinks.classList.remove('open');
          navToggle.setAttribute('aria-expanded', 'false');
          navToggle.textContent = '☰';
        }
      });
    });
  }

  // ── Contact Modal ──
  window.openContactModal = function () {
    if (contactModal) {
      contactModal.style.display = 'flex';
      contactModal.setAttribute('aria-hidden', 'false');
      // Focus first input
      var firstInput = contactModal.querySelector('input, textarea');
      if (firstInput) firstInput.focus();
    }
  };

  window.closeContactModal = function () {
    if (contactModal) {
      contactModal.style.display = 'none';
      contactModal.setAttribute('aria-hidden', 'true');
    }
  };

  // Close modal on overlay click
  if (contactModal) {
    contactModal.addEventListener('click', function (e) {
      if (e.target === contactModal) {
        closeContactModal();
      }
    });
  }

  // Close modal on Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && contactModal && contactModal.style.display === 'flex') {
      closeContactModal();
    }
  });

  // ── Intersection Observer for Fade-In Animations ──
  var fadeEls = document.querySelectorAll('.fade-in');
  if (fadeEls.length > 0 && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );
    fadeEls.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    // Fallback: show everything
    fadeEls.forEach(function (el) {
      el.classList.add('visible');
    });
  }

  // ── Smooth Scroll for Anchor Links ──
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var targetId = this.getAttribute('href');
      if (targetId === '#') return;
      var target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── Service Worker Registration ──
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(function () {
      // Silent fail — non-critical
    });
  }
})();

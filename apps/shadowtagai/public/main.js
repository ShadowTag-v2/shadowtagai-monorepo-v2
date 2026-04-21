/**
 * ShadowTag AI — Main Application Script
 * Handles: nav, modals, toast, intersection observer, scroll progress, smooth scroll
 */

(function () {
  'use strict';

  // ── DOM References ──
  var nav = document.getElementById('main-nav');
  var navToggle = document.getElementById('navToggle');
  var navLinks = document.getElementById('navLinks');
  var contactModal = document.getElementById('contactModal');
  var scrollProgress = document.getElementById('scrollProgress');
  var contactForm = document.getElementById('contactForm');
  var toast = document.getElementById('toast');

  // ── Nav Scroll ──
  function handleNavScroll() {
    if (!nav) return;
    if (window.scrollY > 60) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  }

  // ── Scroll Progress Bar ──
  function handleScrollProgress() {
    if (!scrollProgress) return;
    var docHeight = document.documentElement.scrollHeight - window.innerHeight;
    var progress = docHeight > 0 ? (window.scrollY / docHeight) * 100 : 0;
    scrollProgress.style.width = progress + '%';
  }

  function onScroll() {
    handleNavScroll();
    handleScrollProgress();
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ── Mobile Nav Toggle ──
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      navLinks.classList.toggle('open');
      var isOpen = navLinks.classList.contains('open');
      navToggle.setAttribute('aria-expanded', isOpen);
      navToggle.textContent = isOpen ? '✕' : '☰';
    });

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

  if (contactModal) {
    contactModal.addEventListener('click', function (e) {
      if (e.target === contactModal) closeContactModal();
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && contactModal && contactModal.style.display === 'flex') {
      closeContactModal();
    }
  });

  // ── Toast ──
  function showToast() {
    if (!toast) return;
    toast.classList.add('show');
    setTimeout(function () {
      toast.classList.remove('show');
    }, 4000);
  }

  // ── Contact Form Submit (Google Apps Script) ──
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var formData = new FormData(contactForm);
      fetch(contactForm.action, {
        method: 'POST',
        body: formData
      }).then(function () {
        showToast();
        contactForm.reset();
        closeContactModal();
      }).catch(function () {
        showToast(); // Show success anyway (Google Apps Script CORS quirk)
        contactForm.reset();
        closeContactModal();
      });
    });
  }

  // ── Intersection Observer for Fade-In ──
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
    fadeEls.forEach(function (el) { observer.observe(el); });
  } else {
    fadeEls.forEach(function (el) { el.classList.add('visible'); });
  }

  // ── Smooth Scroll ──
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

  // ── Service Worker ──
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(function () {});
  }
})();

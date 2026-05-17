// apps/shadowtagai/public/js/main.js
// ShadowTagAI Landing Page — UI interactions & scroll animations.
// Extracted from inline <script> block for CSP compliance (Cor.30 R31).

// Mobile nav toggle
const mobileToggle = document.getElementById("mobile-toggle");
const navLinks = document.getElementById("nav-links");
if (mobileToggle) {
  mobileToggle.addEventListener("click", () => {
    navLinks.classList.toggle("nav__links--open");
  });
}

// Scroll-triggered animations
const observerOptions = { threshold: 0.1, rootMargin: "0px 0px -40px 0px" };
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("visible");
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll(".animate-on-scroll").forEach((el) => observer.observe(el));

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach((a) => {
  a.addEventListener("click", (e) => {
    const target = document.querySelector(a.getAttribute("href"));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      navLinks.classList.remove("nav__links--open");
    }
  });
});

// Nav background on scroll
const nav = document.getElementById("main-nav");
window.addEventListener(
  "scroll",
  () => {
    if (window.scrollY > 50) {
      nav.style.background = "rgba(13, 13, 26, 0.95)";
    } else {
      nav.style.background = "";
    }
  },
  { passive: true },
);

// Architecture grid stagger animation
const archGrid = document.getElementById("arch-grid");
if (archGrid) {
  const archObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const cards = archGrid.querySelectorAll(".arch-card");
          cards.forEach((card, i) => {
            card.style.opacity = "0";
            card.style.transform = "translateY(16px)";
            card.style.transition = `all 0.5s ease-out ${i * 0.1}s`;
            requestAnimationFrame(() => {
              card.style.opacity = "1";
              card.style.transform = "translateY(0)";
            });
          });
          archObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.2 },
  );
  archObserver.observe(archGrid);
}

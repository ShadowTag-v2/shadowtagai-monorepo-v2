import "./style.css";

// ═══ SCROLL PROGRESS BAR ═══
const scrollProgress = document.getElementById("scrollProgress");
if (scrollProgress) {
  window.addEventListener(
    "scroll",
    () => {
      const pct = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
      scrollProgress.style.transform = `scaleX(${Math.min(pct, 1)})`;
      scrollProgress.style.width = "100%";
    },
    { passive: true },
  );
}

// ═══ REVEAL ON SCROLL ═══
const reveals = document.querySelectorAll(".reveal");
if (reveals.length) {
  const revealObserver = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          e.target.classList.add("visible");
        }
      }
    },
    { threshold: 0.1 },
  );
  for (const el of reveals) {
    revealObserver.observe(el);
  }
}

// ═══ CONTACT MODAL ═══
const modal = document.getElementById("contactModal");
const toast = document.getElementById("toast");

window.openContactModal = () => {
  if (modal) {
    modal.classList.add("active");
    modal.setAttribute("aria-hidden", "false");
  }
};
window.closeContactModal = () => {
  if (modal) {
    modal.classList.remove("active");
    modal.setAttribute("aria-hidden", "true");
  }
};
if (modal) {
  modal.addEventListener("click", (e) => {
    if (e.target === modal) window.closeContactModal();
  });
}

// Form submission
const form = document.getElementById("contactForm");
if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = new FormData(form);
    if (data.get("_honey")) return;
    const payload = {
      name: data.get("name") || "",
      email: data.get("email") || "",
      company: data.get("company") || "",
      message: data.get("message") || "Inquiry from KovelAI website",
      inquiry_type: data.get("inquiry_type") || "general",
      leadSource: "kovelai.com",
    };
    try {
      await fetch(form.action, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      window.closeContactModal();
      if (toast) {
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 4000);
      }
      form.reset();
    } catch (_err) {
      // Show success anyway — the CF may have processed it despite CORS
      window.closeContactModal();
      if (toast) {
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 4000);
      }
      form.reset();
    }
  });
}

// ═══ NAV SCROLL EFFECT ═══
const nav = document.querySelector(".nav");
if (nav) {
  window.addEventListener(
    "scroll",
    () => {
      nav.style.background = window.scrollY > 50 ? "rgba(17, 15, 9, 0.98)" : "rgba(17, 15, 9, 0.9)";
    },
    { passive: true },
  );
}

// ═══ MOBILE NAV TOGGLE ═══
const navToggle = document.getElementById("navToggle");
const navLinks = document.getElementById("navLinks");
if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    const isOpen = navLinks.style.display === "flex";
    navLinks.style.display = isOpen ? "none" : "flex";
    navToggle.textContent = isOpen ? "☰" : "✕";
  });
  // Close nav on link click (mobile)
  for (const a of navLinks.querySelectorAll("a")) {
    a.addEventListener("click", () => {
      navLinks.style.display = "none";
      navToggle.textContent = "☰";
    });
  }
}

// ═══ SCROLL ENTRANCE OBSERVER ═══
const entranceEls = document.querySelectorAll(".scroll-entrance");
if (entranceEls.length) {
  const entranceObserver = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          e.target.classList.add("entered");
          entranceObserver.unobserve(e.target);
        }
      }
    },
    { threshold: 0.08, rootMargin: "0px 0px -40px 0px" },
  );
  for (const el of entranceEls) {
    entranceObserver.observe(el);
  }
}

// ═══ A/B HEADLINE TEST ═══
const hero = document.getElementById("heroHeadline");
if (hero) {
  const variants = {
    a: `Every Google Search Your Client Makes Is a Loaded Gun Pointed at Your Case.<br/><span class="accent">KovelAI Disarms It — And Bills For the Protection.</span>`,
    b: `After <em>Heppner</em>, Your Clients' Browser History Is Opposing Counsel's Exhibit A.<br/><span class="accent">KovelAI Makes It Disappear — Under Privilege.</span>`,
  };
  const pick = Math.random() < 0.5 ? "a" : "b";
  hero.innerHTML = variants[pick];
  hero.dataset.variant = pick;
}

(() => {
  const e = document.createElement(`link`).relList;
  if (e && e.supports && e.supports(`modulepreload`)) return;
  for (const e of document.querySelectorAll(`link[rel="modulepreload"]`)) n(e);
  new MutationObserver((e) => {
    for (const t of e)
      if (t.type === `childList`)
        for (const e of t.addedNodes) e.tagName === `LINK` && e.rel === `modulepreload` && n(e);
  }).observe(document, { childList: !0, subtree: !0 });
  function t(e) {
    const t = {};
    return (
      e.integrity && (t.integrity = e.integrity),
      e.referrerPolicy && (t.referrerPolicy = e.referrerPolicy),
      e.crossOrigin === `use-credentials`
        ? (t.credentials = `include`)
        : e.crossOrigin === `anonymous`
          ? (t.credentials = `omit`)
          : (t.credentials = `same-origin`),
      t
    );
  }
  function n(e) {
    if (e.ep) return;
    e.ep = !0;
    const n = t(e);
    fetch(e.href, n);
  }
})();
var e = document.getElementById(`scrollProgress`);
e &&
  window.addEventListener(
    `scroll`,
    () => {
      const t = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
      (e.style.transform = `scaleX(${Math.min(t, 1)})`), (e.style.width = `100%`);
    },
    { passive: !0 },
  );
var t = document.getElementById(`particles`);
if (t)
  for (let e = 0; e < 30; e++) {
    const e = document.createElement(`div`);
    (e.className = `particle`),
      (e.style.left = `${Math.random() * 100}%`),
      (e.style.animationDuration = `${8 + Math.random() * 12}s`),
      (e.style.animationDelay = `${Math.random() * 10}s`),
      (e.style.width = e.style.height = `${1 + Math.random() * 2}px`),
      t.appendChild(e);
  }
var n = document.querySelectorAll(`.reveal`);
if (n.length) {
  const e = new IntersectionObserver(
    (e) => {
      e.forEach((e) => {
        e.isIntersecting && e.target.classList.add(`visible`);
      });
    },
    { threshold: 0.1 },
  );
  n.forEach((t) => e.observe(t));
}
var r = document.getElementById(`contactModal`),
  i = document.getElementById(`toast`);
(window.openContactModal = () => {
  r &&
    (r.classList.add(`active`), r.setAttribute(`aria-hidden`, `false`), r.removeAttribute(`inert`));
}),
  (window.closeContactModal = () => {
    r &&
      (r.classList.remove(`active`),
      r.setAttribute(`aria-hidden`, `true`),
      r.setAttribute(`inert`, ``));
  }),
  r &&
    r.addEventListener(`click`, (e) => {
      e.target === r && window.closeContactModal();
    });
var a = document.getElementById(`contactForm`);
a &&
  a.addEventListener(`submit`, async (e) => {
    e.preventDefault();
    const t = new FormData(a);
    if (!t.get(`_honey`))
      try {
        await fetch(a.action, { method: `POST`, body: t }),
          window.closeContactModal(),
          i && (i.classList.add(`show`), setTimeout(() => i.classList.remove(`show`), 4e3)),
          a.reset();
      } catch {}
  });
var o = document.querySelector(`.nav`);
o &&
  window.addEventListener(
    `scroll`,
    () => {
      o.style.background =
        window.scrollY > 50 ? `rgba(15, 19, 31, 0.98)` : `rgba(15, 19, 31, 0.85)`;
    },
    { passive: !0 },
  );
var s = document.getElementById(`navToggle`),
  c = document.getElementById(`navLinks`);
s &&
  c &&
  s.addEventListener(`click`, () => {
    c.style.display = c.style.display === `flex` ? `none` : `flex`;
  });

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
var t = document.querySelectorAll(`.reveal`);
if (t.length) {
  const e = new IntersectionObserver(
    (e) => {
      e.forEach((e) => {
        e.isIntersecting && e.target.classList.add(`visible`);
      });
    },
    { threshold: 0.1 },
  );
  t.forEach((t) => e.observe(t));
}
var n = document.getElementById(`contactModal`),
  r = document.getElementById(`toast`);
(window.openContactModal = () => {
  n && (n.classList.add(`active`), n.setAttribute(`aria-hidden`, `false`));
}),
  (window.closeContactModal = () => {
    n && (n.classList.remove(`active`), n.setAttribute(`aria-hidden`, `true`));
  }),
  n &&
    n.addEventListener(`click`, (e) => {
      e.target === n && window.closeContactModal();
    });
var i = document.getElementById(`contactForm`);
i &&
  i.addEventListener(`submit`, async (e) => {
    e.preventDefault();
    const t = new FormData(i);
    if (!t.get(`_honey`))
      try {
        await fetch(i.action, { method: `POST`, body: t }),
          window.closeContactModal(),
          r && (r.classList.add(`show`), setTimeout(() => r.classList.remove(`show`), 4e3)),
          i.reset();
      } catch {}
  });
var a = document.querySelector(`.nav`);
a &&
  window.addEventListener(
    `scroll`,
    () => {
      a.style.background = window.scrollY > 50 ? `rgba(17, 15, 9, 0.98)` : `rgba(17, 15, 9, 0.9)`;
    },
    { passive: !0 },
  );
var o = document.getElementById(`navToggle`),
  s = document.getElementById(`navLinks`);
o &&
  s &&
  o.addEventListener(`click`, () => {
    s.style.display = s.style.display === `flex` ? `none` : `flex`;
  });

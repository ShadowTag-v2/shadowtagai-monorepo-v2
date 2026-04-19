/**
 * Cloudflare Turnstile CAPTCHA Integration
 *
 * Drop-in Turnstile widget for contact forms.
 *
 * Usage:
 *   1. Add to <head>:
 *      <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit" defer></script>
 *   2. Add before </body>:
 *      <script src="/js/turnstile.js" defer></script>
 *   3. Ensure your form with id="contactForm" has a <div id="turnstile-widget"></div>
 *
 * Configuration:
 *   Set window.TURNSTILE_SITE_KEY before this script loads.
 *   Default: Cloudflare's visible test key for development.
 *
 * The script prevents form submission until Turnstile is solved.
 * Token is included in form submission as cf-turnstile-response.
 *
 * No external dependencies beyond Cloudflare's own script.
 */

(function () {
  "use strict";

  // Site key — use test key in dev, production key in prod
  // Test key always passes: 1x00000000000000000000AA
  // Test key always blocks: 2x00000000000000000000AB
  var isProduction =
    location.hostname === "kovelai.com" ||
    location.hostname === "kovelai.web.app" ||
    location.hostname === "shadowtagai.web.app" ||
    location.hostname === "shadowtag-omega-v4.web.app";

  var SITE_KEY = window.TURNSTILE_SITE_KEY ||
    (isProduction
      ? "0x4AAAAAAAxxxxxxxxxxxxxxxx" // Replace with real Turnstile site key
      : "1x00000000000000000000AA");  // Cloudflare test key (always passes)

  var turnstileToken = null;
  var widgetId = null;

  function injectStyles() {
    var style = document.createElement("style");
    style.textContent = [
      ".cf-turnstile-wrap{margin:12px 0;display:flex;justify-content:center}",
      ".turnstile-error{color:#f87171;font-size:12px;text-align:center;margin-top:4px;display:none}",
    ].join("");
    document.head.appendChild(style);
  }

  function injectWidget() {
    var form = document.getElementById("contactForm");
    if (!form) return false;

    // Check if widget container already exists
    var existing = document.getElementById("turnstile-widget");
    if (existing) return true;

    // Find the submit button and insert before it
    var submitBtn = form.querySelector('button[type="submit"]');
    if (!submitBtn) return false;

    var wrapper = document.createElement("div");
    wrapper.className = "cf-turnstile-wrap";
    wrapper.innerHTML = [
      '<div id="turnstile-widget"></div>',
      '<div class="turnstile-error" id="turnstile-error">Please complete the security check</div>',
    ].join("");

    submitBtn.parentNode.insertBefore(wrapper, submitBtn);
    return true;
  }

  function renderWidget() {
    if (typeof turnstile === "undefined") {
      // Turnstile API not loaded yet — retry
      setTimeout(renderWidget, 200);
      return;
    }

    var container = document.getElementById("turnstile-widget");
    if (!container) return;

    widgetId = turnstile.render(container, {
      sitekey: SITE_KEY,
      theme: "dark",
      callback: function (token) {
        turnstileToken = token;
        var errEl = document.getElementById("turnstile-error");
        if (errEl) errEl.style.display = "none";
      },
      "expired-callback": function () {
        turnstileToken = null;
      },
      "error-callback": function () {
        turnstileToken = null;
      },
    });
  }

  function interceptFormSubmit() {
    var form = document.getElementById("contactForm");
    if (!form) return;

    // Prepend our handler to run before existing handlers
    form.addEventListener(
      "submit",
      function (e) {
        if (!turnstileToken) {
          e.preventDefault();
          e.stopImmediatePropagation();
          var errEl = document.getElementById("turnstile-error");
          if (errEl) errEl.style.display = "block";
          return false;
        }

        // Inject token into form data
        var tokenInput = form.querySelector('input[name="cf-turnstile-response"]');
        if (!tokenInput) {
          tokenInput = document.createElement("input");
          tokenInput.type = "hidden";
          tokenInput.name = "cf-turnstile-response";
          form.appendChild(tokenInput);
        }
        tokenInput.value = turnstileToken;
      },
      true // capture phase — runs before other handlers
    );
  }

  // ── Init ───────────────────────────────────────────────────────────────

  injectStyles();

  // Wait for DOM if needed
  function init() {
    if (injectWidget()) {
      renderWidget();
      interceptFormSubmit();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Also handle dynamically opened modals (contact modal pattern)
  var observer = new MutationObserver(function () {
    var container = document.getElementById("turnstile-widget");
    if (container && !widgetId) {
      renderWidget();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
})();

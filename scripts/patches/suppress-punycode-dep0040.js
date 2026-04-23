/**
 * Antigravity IDE — Deprecation Warning Suppression Patch
 *
 * Intercepts known noisy Node.js deprecation warnings that flood the
 * extension host console:
 *
 *   DEP0040 — `punycode` module (extensions use built-in instead of userland)
 *   DEP0180 — `fs.Stats` constructor (extensions call new fs.Stats() directly)
 *
 * This patch is NON-DESTRUCTIVE: it only suppresses the specific warnings
 * listed in SUPPRESSED_CODES and passes all other warnings/events through
 * unchanged.
 *
 * Applied via NODE_OPTIONS --require in workspace terminal env.
 *
 * @see https://nodejs.org/api/deprecations.html#DEP0040
 * @see https://nodejs.org/api/deprecations.html#DEP0180
 */

const SUPPRESSED_CODES = new Set(['DEP0040', 'DEP0180']);

const originalEmit = process.emit;

process.emit = function (event, ...args) {
  if (event === 'warning') {
    const warning = args[0];
    if (
      warning &&
      typeof warning === 'object' &&
      warning.name === 'DeprecationWarning' &&
      SUPPRESSED_CODES.has(warning.code)
    ) {
      return false;
    }
  }
  return originalEmit.apply(this, [event, ...args]);
};

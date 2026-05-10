/**
 * AgentSpinner — JS Runtime Engine
 * Ported from Claude Code Spinner.tsx + bridgeStatusUtil.ts
 *
 * Drives:
 *  1. Verb cycling from the canonical 190-verb list (4s interval)
 *  2. Stall intensity state machine (normal→warm→hot)
 *  3. Braille glyph rotation (CSS-driven, JS fallback)
 *  4. Optional telemetry hooks
 */

// ── Canonical verb list (from src/constants/spinnerVerbs.ts) ──
const SPINNER_VERBS = [
  'Accomplishing',
  'Actioning',
  'Actualizing',
  'Architecting',
  'Baking',
  'Beaming',
  "Beboppin'",
  'Befuddling',
  'Billowing',
  'Blanching',
  'Bloviating',
  'Boogieing',
  'Boondoggling',
  'Booping',
  'Bootstrapping',
  'Brewing',
  'Bunning',
  'Burrowing',
  'Calculating',
  'Canoodling',
  'Caramelizing',
  'Cascading',
  'Catapulting',
  'Cerebrating',
  'Channeling',
  'Channelling',
  'Choreographing',
  'Churning',
  'Clauding',
  'Coalescing',
  'Cogitating',
  'Combobulating',
  'Composing',
  'Computing',
  'Concocting',
  'Considering',
  'Contemplating',
  'Cooking',
  'Crafting',
  'Creating',
  'Crunching',
  'Crystallizing',
  'Cultivating',
  'Deciphering',
  'Deliberating',
  'Determining',
  'Dilly-dallying',
  'Discombobulating',
  'Doing',
  'Doodling',
  'Drizzling',
  'Ebbing',
  'Effecting',
  'Elucidating',
  'Embellishing',
  'Enchanting',
  'Envisioning',
  'Evaporating',
  'Fermenting',
  'Fiddle-faddling',
  'Finagling',
  'Flambéing',
  'Flibbertigibbeting',
  'Flowing',
  'Flummoxing',
  'Fluttering',
  'Forging',
  'Forming',
  'Frolicking',
  'Frosting',
  'Gallivanting',
  'Galloping',
  'Garnishing',
  'Generating',
  'Gesticulating',
  'Germinating',
  'Gitifying',
  'Grooving',
  'Gusting',
  'Harmonizing',
  'Hashing',
  'Hatching',
  'Herding',
  'Honking',
  'Hullaballooing',
  'Hyperspacing',
  'Ideating',
  'Imagining',
  'Improvising',
  'Incubating',
  'Inferring',
  'Infusing',
  'Ionizing',
  'Jitterbugging',
  'Julienning',
  'Kneading',
  'Leavening',
  'Levitating',
  'Lollygagging',
  'Manifesting',
  'Marinating',
  'Meandering',
  'Metamorphosing',
  'Misting',
  'Moonwalking',
  'Moseying',
  'Mulling',
  'Mustering',
  'Musing',
  'Nebulizing',
  'Nesting',
  'Newspapering',
  'Noodling',
  'Nucleating',
  'Orbiting',
  'Orchestrating',
  'Osmosing',
  'Perambulating',
  'Percolating',
  'Perusing',
  'Philosophising',
  'Photosynthesizing',
  'Pollinating',
  'Pondering',
  'Pontificating',
  'Pouncing',
  'Precipitating',
  'Prestidigitating',
  'Processing',
  'Proofing',
  'Propagating',
  'Puttering',
  'Puzzling',
  'Quantumizing',
  'Razzle-dazzling',
  'Razzmatazzing',
  'Recombobulating',
  'Reticulating',
  'Roosting',
  'Ruminating',
  'Sautéing',
  'Scampering',
  'Schlepping',
  'Scurrying',
  'Seasoning',
  'Shenaniganing',
  'Shimmying',
  'Simmering',
  'Skedaddling',
  'Sketching',
  'Slithering',
  'Smooshing',
  'Sock-hopping',
  'Spelunking',
  'Spinning',
  'Sprouting',
  'Stewing',
  'Sublimating',
  'Swirling',
  'Swooping',
  'Symbioting',
  'Synthesizing',
  'Tempering',
  'Thinking',
  'Thundering',
  'Tinkering',
  'Tomfoolering',
  'Topsy-turvying',
  'Transfiguring',
  'Transmuting',
  'Twisting',
  'Undulating',
  'Unfurling',
  'Unravelling',
  'Vibing',
  'Waddling',
  'Wandering',
  'Warping',
  'Whatchamacalliting',
  'Whirlpooling',
  'Whirring',
  'Whisking',
  'Wibbling',
  'Working',
  'Wrangling',
  'Zesting',
  'Zigzagging',
];

// ── Stall thresholds (from Claude Code Spinner.tsx) ──
const STALL_NORMAL_MS = 10_000;
const STALL_WARM_MS = 30_000;
const VERB_CYCLE_MS = 4_000;

/**
 * Fisher-Yates shuffle (in-place).
 * @param {string[]} arr
 * @returns {string[]}
 */
function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

/**
 * Create an AgentSpinner controller bound to a DOM element.
 *
 * @param {HTMLElement} container - Must have class `agent-spinner`.
 * @param {object} [opts]
 * @param {number} [opts.verbCycleMs=4000] - Interval between verb swaps.
 * @param {string[]} [opts.verbs] - Override verb list.
 * @param {function} [opts.onStallChange] - Callback on stall state change.
 * @returns {{ start: function, stop: function, destroy: function }}
 */
function createAgentSpinner(container, opts = {}) {
  const verbCycleMs = opts.verbCycleMs || VERB_CYCLE_MS;
  const verbs = opts.verbs || shuffle([...SPINNER_VERBS]);
  const onStallChange = opts.onStallChange || null;

  // ── DOM Discovery ──
  const verbEl = container.querySelector('.agent-spinner__verb');
  const verbWrapEl = container.querySelector('.agent-spinner__verb-wrap');

  let verbIndex = 0;
  let verbTimer = null;
  let stallTimer = null;
  let startTime = 0;
  let currentStall = 'normal';

  function setVerb(text) {
    if (!verbEl) return;
    // If we have a verb-wrap with enter/exit transitions
    if (verbWrapEl) {
      const inner = verbWrapEl.querySelector('.agent-spinner__verb-inner');
      if (inner) {
        inner.setAttribute('data-state', 'exiting');
        setTimeout(() => {
          verbEl.textContent = text;
          inner.setAttribute('data-state', 'entering');
        }, 250);
        return;
      }
    }
    verbEl.textContent = text;
  }

  function cycleVerb() {
    verbIndex = (verbIndex + 1) % verbs.length;
    setVerb(verbs[verbIndex]);
  }

  function updateStall() {
    const elapsed = Date.now() - startTime;
    let next = 'normal';
    if (elapsed > STALL_WARM_MS) {
      next = 'hot';
    } else if (elapsed > STALL_NORMAL_MS) {
      next = 'warm';
    }
    if (next !== currentStall) {
      currentStall = next;
      container.setAttribute('data-stall', next);
      if (onStallChange) onStallChange(next, elapsed);
    }
  }

  function start() {
    startTime = Date.now();
    currentStall = 'normal';
    container.setAttribute('data-stall', 'normal');
    verbIndex = 0;
    setVerb(verbs[0]);

    // Verb cycling
    verbTimer = setInterval(cycleVerb, verbCycleMs);
    // Stall intensity check every second
    stallTimer = setInterval(updateStall, 1_000);

    container.style.display = '';
    container.removeAttribute('hidden');
  }

  function stop() {
    if (verbTimer) {
      clearInterval(verbTimer);
      verbTimer = null;
    }
    if (stallTimer) {
      clearInterval(stallTimer);
      stallTimer = null;
    }
    currentStall = 'normal';
    container.setAttribute('data-stall', 'normal');
  }

  function destroy() {
    stop();
    container.style.display = 'none';
  }

  return { start, stop, destroy, getVerbs: () => verbs };
}

// ── HTML Template Generator ──
/**
 * Generate the innerHTML for an AgentSpinner.
 * @param {object} [opts]
 * @param {string} [opts.theme] - 'shadowtag' | 'kovelai' | 'headfade'
 * @param {boolean} [opts.overlay] - Full overlay mode
 * @param {string} [opts.label] - Overlay label text
 * @returns {string} HTML string
 */
function agentSpinnerHTML(opts = {}) {
  const theme = opts.theme ? ` agent-spinner--${opts.theme}` : '';
  const overlay = opts.overlay ? ' agent-spinner--overlay' : '';
  const label = opts.label || '';

  return `<div class="agent-spinner${theme}${overlay}" data-stall="normal" role="status" aria-live="polite" aria-label="Loading">
  <span class="agent-spinner__glyph" aria-hidden="true">⠋</span>
  <div class="agent-spinner__verb-wrap">
    <div class="agent-spinner__verb-inner" data-state="entering">
      <span class="agent-spinner__verb">Initializing</span>
    </div>
  </div>
  <span class="agent-spinner__dots" aria-hidden="true"></span>
  ${label ? `<span class="agent-spinner__label">${label}</span>` : ''}
</div>`;
}

// ── Exports (ESM + UMD compatible) ──
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { createAgentSpinner, agentSpinnerHTML, SPINNER_VERBS };
}
if (typeof window !== 'undefined') {
  window.AgentSpinner = { createAgentSpinner, agentSpinnerHTML, SPINNER_VERBS };
}

export { agentSpinnerHTML, createAgentSpinner, SPINNER_VERBS };

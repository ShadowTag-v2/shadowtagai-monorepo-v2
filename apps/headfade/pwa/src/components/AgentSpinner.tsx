'use client';
import { useCallback, useEffect, useRef, useState } from 'react';

/* ═══════════════════════════════════════════════════════════════
   AgentSpinner — React Component
   Ported from Claude Code Spinner.tsx patterns
   
   Usage:
     <AgentSpinner theme="headfade" active={isLoading} label="FORENSIC ANALYSIS" />
     <AgentSpinner theme="kovelai" active={isLoading} overlay />
   ═══════════════════════════════════════════════════════════════ */

// ── Canonical verb list (inlined to avoid cross-package dep) ──
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
  'Choreographing',
  'Churning',
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
  'Fermenting',
  'Finagling',
  'Flambéing',
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
  'Grooving',
  'Gusting',
  'Harmonizing',
  'Hashing',
  'Hatching',
  'Herding',
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
  'Kneading',
  'Leavening',
  'Levitating',
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
  'Noodling',
  'Nucleating',
  'Orbiting',
  'Orchestrating',
  'Osmosing',
  'Percolating',
  'Perusing',
  'Philosophising',
  'Pollinating',
  'Pondering',
  'Pontificating',
  'Precipitating',
  'Prestidigitating',
  'Processing',
  'Proofing',
  'Propagating',
  'Puttering',
  'Puzzling',
  'Quantumizing',
  'Razzle-dazzling',
  'Recombobulating',
  'Reticulating',
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
  'Spelunking',
  'Spinning',
  'Sprouting',
  'Stewing',
  'Sublimating',
  'Swirling',
  'Swooping',
  'Synthesizing',
  'Tempering',
  'Thinking',
  'Thundering',
  'Tinkering',
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
  'Whirlpooling',
  'Whirring',
  'Whisking',
  'Wibbling',
  'Working',
  'Wrangling',
  'Zesting',
  'Zigzagging',
];

// Braille spinner frames (Claude Code canonical)
const BRAILLE_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧'];
const FRAME_INTERVAL = 125;
const VERB_CYCLE_MS = 4_000;
const STALL_NORMAL_MS = 10_000;
const STALL_WARM_MS = 30_000;

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/**
 * AgentSpinner React component.
 *
 * @param {object} props
 * @param {boolean} props.active - Show/hide the spinner
 * @param {'shadowtag'|'kovelai'|'headfade'} [props.theme] - Theme variant
 * @param {boolean} [props.overlay] - Full overlay mode
 * @param {string} [props.label] - Extra label text
 * @param {string} [props.className] - Additional CSS classes
 * @param {function} [props.onStallChange] - Callback(stallLevel, elapsedMs)
 */
interface AgentSpinnerProps {
  active?: boolean;
  theme?: 'shadowtag' | 'kovelai' | 'headfade';
  overlay?: boolean;
  label?: string;
  className?: string;
  onStallChange?: (stallLevel: string, elapsedMs: number) => void;
}

export default function AgentSpinner({
  active = false,
  theme,
  overlay = false,
  label,
  className = '',
  onStallChange,
}: AgentSpinnerProps) {
  const [verb, setVerb] = useState('Initializing');
  const [verbState, setVerbState] = useState('entering');
  const [frame, setFrame] = useState(0);
  const [stall, setStall] = useState('normal');
  const [dots, setDots] = useState('.');

  const startTimeRef = useRef(0);
  const verbsRef = useRef(shuffle(SPINNER_VERBS));
  const verbIndexRef = useRef(0);
  const frameRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const verbTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const stallTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const dotsTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const cycleVerb = useCallback(() => {
    setVerbState('exiting');
    setTimeout(() => {
      verbIndexRef.current = (verbIndexRef.current + 1) % verbsRef.current.length;
      setVerb(verbsRef.current[verbIndexRef.current]);
      setVerbState('entering');
    }, 250);
  }, []);

  useEffect(() => {
    if (!active) {
      // Cleanup all timers
      if (frameRef.current) clearInterval(frameRef.current);
      if (verbTimerRef.current) clearInterval(verbTimerRef.current);
      if (stallTimerRef.current) clearInterval(stallTimerRef.current);
      if (dotsTimerRef.current) clearInterval(dotsTimerRef.current);
      setStall('normal');
      return;
    }

    // Reset state
    startTimeRef.current = Date.now();
    verbIndexRef.current = 0;
    verbsRef.current = shuffle(SPINNER_VERBS);
    setVerb(verbsRef.current[0]);
    setVerbState('entering');
    setStall('normal');
    setFrame(0);

    // Braille frame rotation
    frameRef.current = setInterval(() => {
      setFrame((f) => (f + 1) % BRAILLE_FRAMES.length);
    }, FRAME_INTERVAL);

    // Verb cycling
    verbTimerRef.current = setInterval(cycleVerb, VERB_CYCLE_MS);

    // Dots cycling
    const dotFrames = ['.', '..', '...'];
    let dotIdx = 0;
    dotsTimerRef.current = setInterval(() => {
      dotIdx = (dotIdx + 1) % dotFrames.length;
      setDots(dotFrames[dotIdx]);
    }, 500);

    // Stall intensity
    stallTimerRef.current = setInterval(() => {
      const elapsed = Date.now() - startTimeRef.current;
      let next = 'normal';
      if (elapsed > STALL_WARM_MS) next = 'hot';
      else if (elapsed > STALL_NORMAL_MS) next = 'warm';
      setStall((prev) => {
        if (prev !== next) {
          onStallChange?.(next, elapsed);
        }
        return next;
      });
    }, 1_000);

    return () => {
      if (frameRef.current) clearInterval(frameRef.current);
      if (verbTimerRef.current) clearInterval(verbTimerRef.current);
      if (stallTimerRef.current) clearInterval(stallTimerRef.current);
      if (dotsTimerRef.current) clearInterval(dotsTimerRef.current);
    };
  }, [active, cycleVerb, onStallChange]);

  if (!active) return null;

  const themeClass = theme ? ` agent-spinner--${theme}` : '';
  const overlayClass = overlay ? ' agent-spinner--overlay' : '';

  return (
    <div
      className={`agent-spinner${themeClass}${overlayClass} ${className}`}
      data-stall={stall}
      role="status"
      aria-live="polite"
      aria-label="Loading"
    >
      <span className="agent-spinner__glyph" aria-hidden="true">
        {BRAILLE_FRAMES[frame]}
      </span>
      <div className="agent-spinner__verb-wrap">
        <div className="agent-spinner__verb-inner" data-state={verbState}>
          <span className="agent-spinner__verb">{verb}</span>
        </div>
      </div>
      <span className="agent-spinner__dots" aria-hidden="true">
        {dots}
      </span>
      {label && <span className="agent-spinner__label">{label}</span>}
    </div>
  );
}

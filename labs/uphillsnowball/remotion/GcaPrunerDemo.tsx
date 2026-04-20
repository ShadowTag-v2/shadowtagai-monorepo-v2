/**
 * Remotion Video Demo — GCA State DB Pruner
 *
 * Renders an animated terminal sequence showing:
 * 1. The diagnostic output (26.7MB bloat discovery)
 * 2. The fix (--write mode prune + VACUUM)
 * 3. The before/after metrics
 *
 * Usage:
 *   npx remotion render src/GcaPrunerDemo.tsx GcaPrunerDemo out/gca-demo.mp4
 *
 * Requires: npm install remotion @remotion/cli
 */

import {
  AbsoluteFill,
  interpolate,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

const FONT = 'JetBrains Mono, SF Mono, Consolas, monospace';

const TerminalLine = ({ text, delay, color = '#e0e0e0' }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame - delay, [0, 8], [0, 1], { extrapolateRight: 'clamp' });
  const chars = Math.floor(
    interpolate(frame - delay, [0, 20], [0, text.length], { extrapolateRight: 'clamp' }),
  );

  if (frame < delay) return null;

  return (
    <div style={{ fontFamily: FONT, fontSize: 22, color, opacity, lineHeight: 1.6 }}>
      {text.substring(0, chars)}
      {chars < text.length && <span style={{ opacity: frame % 10 < 5 ? 1 : 0 }}>▌</span>}
    </div>
  );
};

const DiagnosticScene = () => (
  <AbsoluteFill style={{ backgroundColor: '#1e1e2e', padding: 60 }}>
    <TerminalLine text="$ python3 prune_gca_chat_threads.py --dry-run" delay={0} color="#a6e3a1" />
    <TerminalLine text="" delay={15} />
    <TerminalLine text="State DB: ~/Library/.../state.vscdb" delay={20} color="#89b4fa" />
    <TerminalLine text="File size: 59,723,776 bytes" delay={30} color="#f38ba8" />
    <TerminalLine text="" delay={35} />
    <TerminalLine text="GCA state total:       26,723,331 bytes" delay={40} color="#fab387" />
    <TerminalLine text="chatThreads payload:   26,857,757 bytes" delay={50} color="#f38ba8" />
    <TerminalLine text="Thread count:                    1" delay={60} color="#cdd6f4" />
    <TerminalLine text="Other preserved keys:           18" delay={70} color="#a6e3a1" />
    <TerminalLine text="" delay={75} />
    <TerminalLine
      text='Preserved keys: ["Error: ENOENT... at Object.Date"]'
      delay={80}
      color="#f38ba8"
    />
    <TerminalLine text="" delay={95} />
    <TerminalLine
      text="🤯 It's deserializing this into RAM on every load."
      delay={100}
      color="#cba6f7"
    />
  </AbsoluteFill>
);

const FixScene = () => (
  <AbsoluteFill style={{ backgroundColor: '#1e1e2e', padding: 60 }}>
    <TerminalLine text="$ python3 prune_gca_chat_threads.py --write" delay={0} color="#a6e3a1" />
    <TerminalLine text="" delay={10} />
    <TerminalLine text="──── WRITE MODE ────" delay={15} color="#cdd6f4" />
    <TerminalLine
      text="Backup created: state.vscdb.backup.20260416T212001"
      delay={25}
      color="#89b4fa"
    />
    <TerminalLine text="" delay={30} />
    <TerminalLine text="📉 Before:    26,723,331 bytes" delay={35} color="#f38ba8" />
    <TerminalLine text="🔥 After:          5,228 bytes" delay={50} color="#a6e3a1" />
    <TerminalLine text="⚡ Freed:     26,718,103 bytes" delay={65} color="#f9e2af" />
    <TerminalLine text="   Threads:   26,857,757 → 2 bytes" delay={75} color="#cdd6f4" />
    <TerminalLine text="" delay={80} />
    <TerminalLine
      text="Running VACUUM to reclaim SQLite dead space..."
      delay={85}
      color="#89b4fa"
    />
    <TerminalLine text="   DB file before: 59,723,776 bytes" delay={95} color="#f38ba8" />
    <TerminalLine text="   DB file after:   1,228,800 bytes" delay={105} color="#a6e3a1" />
    <TerminalLine text="   Disk reclaimed: 58,494,976 bytes" delay={115} color="#f9e2af" />
    <TerminalLine text="" delay={120} />
    <TerminalLine text="✅ Successfully pruned. IDE speed restored." delay={125} color="#a6e3a1" />
  </AbsoluteFill>
);

export const GcaPrunerDemo = () => (
  <AbsoluteFill>
    <Sequence from={0} durationInFrames={150}>
      <DiagnosticScene />
    </Sequence>
    <Sequence from={150} durationInFrames={180}>
      <FixScene />
    </Sequence>
  </AbsoluteFill>
);

// Remotion config
export const RemotionRoot = () => <GcaPrunerDemo />;

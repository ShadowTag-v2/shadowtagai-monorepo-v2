import type React from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

/* ═══════════════════════════════════════════════════════════════════════════
   CounselConduit – Sales Demo Video (15 seconds @ 30fps = 450 frames)
   
   Scene breakdown:
     0–90    Intro / brand reveal
     91–180  Problem statement
     181–300 Product showcase (3 features)
     301–390 Pricing / CTA
     391–450 Logo + tagline
   ═══════════════════════════════════════════════════════════════════════════ */

const COLORS = {
  bg: '#0a0a1a',
  bgGradient: 'linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0a0a1a 100%)',
  primary: '#6366f1',
  primaryLight: '#818cf8',
  accent: '#22d3ee',
  text: '#f1f5f9',
  textMuted: '#94a3b8',
  gold: '#fbbf24',
};

// ── Shared components ──────────────────────────────────────────────────────

const FadeIn: React.FC<{
  children: React.ReactNode;
  delay?: number;
  duration?: number;
}> = ({ children, delay = 0, duration = 20 }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame - delay, [0, duration], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const y = interpolate(frame - delay, [0, duration], [30, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  return <div style={{ opacity, transform: `translateY(${y}px)` }}>{children}</div>;
};

const GlowOrb: React.FC<{
  x: number;
  y: number;
  size: number;
  color: string;
}> = ({ x, y, size, color }) => {
  const frame = useCurrentFrame();
  const pulse = Math.sin(frame * 0.03) * 10;
  return (
    <div
      style={{
        position: 'absolute',
        left: `${x}%`,
        top: `${y}%`,
        width: size + pulse,
        height: size + pulse,
        borderRadius: '50%',
        background: `radial-gradient(circle, ${color}40 0%, transparent 70%)`,
        filter: 'blur(40px)',
      }}
    />
  );
};

// ── Scene 1: Intro ─────────────────────────────────────────────────────────

const IntroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 12 } });
  const titleOpacity = interpolate(frame, [20, 50], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        background: COLORS.bgGradient,
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <GlowOrb x={20} y={30} size={300} color={COLORS.primary} />
      <GlowOrb x={70} y={60} size={250} color={COLORS.accent} />
      <div style={{ textAlign: 'center', transform: `scale(${scale})` }}>
        <div
          style={{
            fontSize: 72,
            fontWeight: 800,
            color: COLORS.text,
            fontFamily: 'Inter, sans-serif',
            letterSpacing: '-2px',
            opacity: titleOpacity,
          }}
        >
          Counsel
          <span style={{ color: COLORS.primary }}>Conduit</span>
        </div>
        <FadeIn delay={40}>
          <div
            style={{
              fontSize: 28,
              color: COLORS.textMuted,
              marginTop: 16,
              fontFamily: 'Inter, sans-serif',
              fontWeight: 400,
            }}
          >
            The Shopify for Legal AI
          </div>
        </FadeIn>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 2: Problem ───────────────────────────────────────────────────────

const ProblemScene: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        background: COLORS.bgGradient,
        justifyContent: 'center',
        alignItems: 'center',
        padding: '0 120px',
      }}
    >
      <GlowOrb x={80} y={20} size={200} color="#ef4444" />
      <div style={{ textAlign: 'center' }}>
        <FadeIn delay={5}>
          <div
            style={{
              fontSize: 48,
              fontWeight: 700,
              color: COLORS.text,
              fontFamily: 'Inter, sans-serif',
              lineHeight: 1.3,
            }}
          >
            Law firms lose <span style={{ color: '#ef4444' }}>attorney-client privilege</span>
            <br />
            when using consumer AI tools.
          </div>
        </FadeIn>
        <FadeIn delay={30}>
          <div
            style={{
              fontSize: 24,
              color: COLORS.textMuted,
              marginTop: 32,
              fontFamily: 'Inter, sans-serif',
              maxWidth: 800,
              margin: '32px auto 0',
            }}
          >
            ChatGPT, Claude, and Gemini don't preserve the Kovel attestation chain required for
            privileged legal research.
          </div>
        </FadeIn>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 3: Product ───────────────────────────────────────────────────────

const features = [
  {
    icon: '🔒',
    title: 'Privilege-Preserving',
    desc: 'Kovel attestation receipts with HMAC-SHA256 cryptographic hashes',
  },
  {
    icon: '⚡',
    title: 'Multi-Model Routing',
    desc: 'Gemini, Claude, GPT-4, Grok — one portal, all models',
  },
  {
    icon: '🛡️',
    title: 'Judge #6 Policy Gate',
    desc: 'Mandatory compliance layer on every query, every response',
  },
];

const ProductScene: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        background: COLORS.bgGradient,
        justifyContent: 'center',
        alignItems: 'center',
        padding: '0 80px',
      }}
    >
      <GlowOrb x={10} y={50} size={200} color={COLORS.primary} />
      <GlowOrb x={90} y={30} size={180} color={COLORS.accent} />
      <div>
        <FadeIn delay={5}>
          <div
            style={{
              fontSize: 42,
              fontWeight: 700,
              color: COLORS.text,
              fontFamily: 'Inter, sans-serif',
              textAlign: 'center',
              marginBottom: 48,
            }}
          >
            Built for law firms. Protected by law.
          </div>
        </FadeIn>
        <div style={{ display: 'flex', gap: 32, justifyContent: 'center' }}>
          {features.map((f, i) => (
            <FadeIn key={i} delay={20 + i * 25}>
              <div
                style={{
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: 16,
                  padding: '40px 32px',
                  width: 320,
                  backdropFilter: 'blur(20px)',
                }}
              >
                <div style={{ fontSize: 48, marginBottom: 16 }}>{f.icon}</div>
                <div
                  style={{
                    fontSize: 22,
                    fontWeight: 600,
                    color: COLORS.text,
                    fontFamily: 'Inter, sans-serif',
                    marginBottom: 12,
                  }}
                >
                  {f.title}
                </div>
                <div
                  style={{
                    fontSize: 16,
                    color: COLORS.textMuted,
                    fontFamily: 'Inter, sans-serif',
                    lineHeight: 1.5,
                  }}
                >
                  {f.desc}
                </div>
              </div>
            </FadeIn>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 4: Pricing CTA ──────────────────────────────────────────────────

const PricingScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const buttonScale = spring({ frame: frame - 40, fps, config: { damping: 8 } });

  return (
    <AbsoluteFill
      style={{
        background: COLORS.bgGradient,
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <GlowOrb x={50} y={20} size={400} color={COLORS.primary} />
      <div style={{ textAlign: 'center' }}>
        <FadeIn delay={5}>
          <div
            style={{
              fontSize: 20,
              color: COLORS.gold,
              fontFamily: 'Inter, sans-serif',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: 3,
              marginBottom: 16,
            }}
          >
            Launch Special
          </div>
        </FadeIn>
        <FadeIn delay={15}>
          <div
            style={{
              fontSize: 64,
              fontWeight: 800,
              color: COLORS.text,
              fontFamily: 'Inter, sans-serif',
            }}
          >
            50% off for 3 months
          </div>
        </FadeIn>
        <FadeIn delay={25}>
          <div
            style={{
              fontSize: 24,
              color: COLORS.textMuted,
              marginTop: 16,
              fontFamily: 'Inter, sans-serif',
            }}
          >
            Solo $149/mo · Practice $299/mo · Enterprise $999/mo
          </div>
        </FadeIn>
        <div
          style={{
            transform: `scale(${buttonScale})`,
            marginTop: 40,
          }}
        >
          <div
            style={{
              display: 'inline-block',
              background: `linear-gradient(135deg, ${COLORS.primary}, ${COLORS.accent})`,
              color: COLORS.text,
              fontSize: 22,
              fontWeight: 700,
              padding: '18px 48px',
              borderRadius: 12,
              fontFamily: 'Inter, sans-serif',
            }}
          >
            Start Free Trial →
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 5: Logo outro ───────────────────────────────────────────────────

const OutroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 15 } });

  return (
    <AbsoluteFill
      style={{
        background: COLORS.bg,
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <GlowOrb x={50} y={50} size={500} color={COLORS.primary} />
      <div style={{ textAlign: 'center', transform: `scale(${scale})` }}>
        <div
          style={{
            fontSize: 56,
            fontWeight: 800,
            color: COLORS.text,
            fontFamily: 'Inter, sans-serif',
          }}
        >
          Counsel
          <span style={{ color: COLORS.primary }}>Conduit</span>
        </div>
        <div
          style={{
            fontSize: 20,
            color: COLORS.textMuted,
            fontFamily: 'Inter, sans-serif',
            marginTop: 12,
          }}
        >
          counselconduit.com
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Main composition ──────────────────────────────────────────────────────

export const CounselConduitDemo: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      <Sequence from={0} durationInFrames={90}>
        <IntroScene />
      </Sequence>
      <Sequence from={90} durationInFrames={90}>
        <ProblemScene />
      </Sequence>
      <Sequence from={180} durationInFrames={120}>
        <ProductScene />
      </Sequence>
      <Sequence from={300} durationInFrames={90}>
        <PricingScene />
      </Sequence>
      <Sequence from={390} durationInFrames={60}>
        <OutroScene />
      </Sequence>
    </AbsoluteFill>
  );
};

#!/usr/bin/env node
/**
 * Remotion Video PR Demo Configuration
 *
 * Defines the Remotion composition for programmatic demo reels
 * using Veo 3.1 generated clips.
 *
 * Prerequisites:
 *   npm install -g remotion
 *   npx remotion render src/index.tsx DemoReel out/demo.mp4
 *
 * Task #5
 */

import { Composition, registerRoot } from 'remotion';

const DemoReel = () => {
  // Video clips from Veo pipeline
  const clips = [
    { src: '/veo-output/hero_drift_0.mp4', label: 'Hero Drift', duration: 240 },
    { src: '/veo-output/counselconduit_hero_0.mp4', label: 'CounselConduit', duration: 240 },
    { src: '/veo-output/onboarding_flow_0.mp4', label: 'Onboarding', duration: 240 },
    { src: '/veo-output/billing_explainer_0.mp4', label: 'Billing', duration: 240 },
    { src: '/veo-output/stripe_webhook_0.mp4', label: 'Webhooks', duration: 240 },
    { src: '/veo-output/shadowtagai_marketing_0.mp4', label: 'Marketing', duration: 240 },
  ];

  return (
    <>
      {clips.map((clip, i) => (
        <Composition
          key={clip.label}
          id={clip.label.replace(/\s/g, '')}
          component={() => (
            <div
              style={{
                width: '100%',
                height: '100%',
                background: '#0a0a0f',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <video
                src={clip.src}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                autoPlay
                muted
              />
              <div
                style={{
                  position: 'absolute',
                  bottom: 40,
                  left: 40,
                  color: '#f0f0f5',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 24,
                  fontWeight: 700,
                  textShadow: '0 2px 10px rgba(0,0,0,0.8)',
                }}
              >
                {clip.label}
              </div>
            </div>
          )}
          durationInFrames={clip.duration}
          fps={30}
          width={1280}
          height={720}
        />
      ))}
    </>
  );
};

registerRoot(DemoReel);

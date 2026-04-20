import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}', './components/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        void: '#05020A', // Deepest Violet-Black (Bg)
        surface: '#0E0B16', // Obsidian Violet (Card)
        tension: '#2A2438', // Low-contrast Violet (Border)
        starlight: '#F4F0FF', // White with a lavender ghost (Text)
        brand: {
          DEFAULT: '#6E56CF', // Electric Violet
          glow: '#B28CFF', // Lighter accent
        },
        burn: '#FF4F00', // International Orange (Status/Money)
        ghost: '#888888', // Metadata
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace'], // The aesthetic of "Truth"
        sans: ['"Inter"', 'sans-serif'], // The aesthetic of "UI"
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
};
export default config;

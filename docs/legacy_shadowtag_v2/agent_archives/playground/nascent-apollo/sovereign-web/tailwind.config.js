/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        void: '#000000', // PURE BLACK for OLED/Depth
        surface: '#0A0A0A', // Subtle separation
        tension: '#262626', // Structural lines
        starlight: '#EDEDED', // Primary text
        ghost: '#888888', // Metadata
        accent: '#6E56CF', // Electric Violet (The Soul)
        burn: '#FF4F00', // International Orange (Risk/Cost)
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'grid-pattern': "url(\"data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h40v40H0V0zm1 1h38v38H1V1z' fill='%23262626' fill-opacity='0.1' fill-rule='evenodd'/%3E%3C/svg%3E\")",
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #6E56CF' },
          '100%': { boxShadow: '0 0 20px #6E56CF, 0 0 10px #6E56CF' },
        }
      }
    },
  },
  plugins: [],
}

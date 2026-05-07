import type { Config } from 'tailwindcss';
import plugin from 'tailwindcss/plugin';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f4fcff',
          100: '#e0f8ff',
          200: '#b8efff',
          300: '#7ae1ff',
          400: '#33d1ff',
          500: '#00b9fa',
          600: '#0093d6',
          700: '#0274ac',
          800: '#04628f',
          900: '#0a5175',
          950: '#063550',
        },
        tinted: {
          50: '#f6f9fc',
          100: '#eef3f8',
          200: '#dee7f1',
          300: '#c5d5e5',
          400: '#a6bdd1',
          500: '#849fba',
          600: '#6984a3',
          700: '#546b86',
          800: '#46586e',
          900: '#3d4a5b',
          950: '#28313e',
        },
        luxury: {
          900: '#0a0a0f',
          800: '#121218',
          700: '#1a1a24',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      screens: {
        '3xl': '1920px',
        '4xl': '2560px',
      },
    },
  },
  plugins: [
    plugin(function ({ addUtilities }) {
      addUtilities({
        '.scrollbar-hide': {
          '-ms-overflow-style': 'none',
          'scrollbar-width': 'none',
          '&::-webkit-scrollbar': {
            display: 'none',
          },
        },
      });
    }),
  ],
};

export default config;

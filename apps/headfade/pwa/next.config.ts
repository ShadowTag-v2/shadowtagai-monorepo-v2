import type { NextConfig } from 'next';

const config: NextConfig = {
  output: 'export',
  reactStrictMode: true,
  transpilePackages: ['@packages/ui'],
  images: {
    unoptimized: true,
  },
};

export default config;

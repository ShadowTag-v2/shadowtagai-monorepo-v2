import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Static export for Firebase Hosting deployment
  output: 'export',
  distDir: '../public',
  images: {
    unoptimized: true,
  },
};

export default nextConfig;

import type { NextConfig } from 'next';

const isProd = process.env.NODE_ENV === 'production';

const nextConfig: NextConfig = {
  // Static export for Firebase Hosting deployment
  ...(isProd && { output: 'export', distDir: '../public' }),
  images: {
    unoptimized: true,
  },
};

export default nextConfig;

import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn-sites-assets.mziq.com',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;

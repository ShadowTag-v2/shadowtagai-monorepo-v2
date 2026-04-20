import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },

  // Intercept the annoying Unleash proxy calls and send them into a void
  async rewrites() {
    return [
      {
        source: '/proxy/unleash/:path*',
        destination: '/api/blackhole',
      },
    ];
  },
};

export default nextConfig;

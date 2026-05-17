import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Turbopack (Next.js 16) forbids distDir outside project path.
  // Build output goes here, then post-build script copies to ../public.
  distDir: ".next-export",
  images: {
    unoptimized: true,
  },
  turbopack: {
    root: __dirname,
  },
};

export default nextConfig;

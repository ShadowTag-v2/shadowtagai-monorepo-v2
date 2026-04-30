/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["@kovelai/ui"], // Solves Problem 2: Monorepo UI invalidation
  experimental: {
    turbo: {
      resolveAlias: {
        "@/*": ["./src/*"],
      },
    },
  },
};

export default nextConfig;

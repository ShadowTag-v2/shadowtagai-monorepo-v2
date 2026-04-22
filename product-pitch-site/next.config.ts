import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  /* Static export for Firebase Hosting — no Node.js server needed */
};

export default nextConfig;

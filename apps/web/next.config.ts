import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@axorks/types", "@axorks/utils", "@axorks/ui"],
};

export default nextConfig;

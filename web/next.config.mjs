/** @type {import('next').NextConfig} */
const apiOrigin = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const nextConfig = {
  output: "standalone",
  async redirects() {
    return [
      {
        source: "/index",
        destination: "/",
        permanent: false,
      },
    ];
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiOrigin}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;

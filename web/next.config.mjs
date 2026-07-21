/** @type {import('next').NextConfig} */
const nextConfig = {
  // Fully static export — deploys to Vercel (or any static host) with no server.
  // The Journey is generated at build time from the committed collection.json.
  output: "export",
  images: { unoptimized: true },
};
export default nextConfig;

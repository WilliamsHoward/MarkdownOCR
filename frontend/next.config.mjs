/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Ensure that the output is compatible with the Docker build if using standalone
  // output: 'standalone',
};

export default nextConfig;

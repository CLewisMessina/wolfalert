/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  typescript: {
    // Type checking happens in separate step
    ignoreBuildErrors: false,
  },
  eslint: {
    // Linting happens in separate step
    ignoreDuringBuilds: false,
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ]
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ]
  },
  images: {
    domains: [
      'avatars.githubusercontent.com',
      'images.unsplash.com',
    ],
    formats: ['image/webp', 'image/avif'],
  },
  // Performance optimizations
  swcMinify: true,
  compress: true,
  poweredByHeader: false,
}

module.exports = nextConfig
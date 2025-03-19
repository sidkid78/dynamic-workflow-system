/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: [], // Only add specific domains you need
    dangerouslyAllowSVG: true,
    contentDispositionType: 'attachment',
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
  serverExternalPackages: [],
}

module.exports = nextConfig 
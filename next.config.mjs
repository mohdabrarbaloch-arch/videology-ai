

const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**.supabase.co' },
      { protocol: 'https', hostname: 'oaidalleapiprodscus.blob.core.windows.net' },
    ],
  },
  experimental: {
    serverActions: { bodySizeLimit: '500mb' },
  },
}

export default nextConfig

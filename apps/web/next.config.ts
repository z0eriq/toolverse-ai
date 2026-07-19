import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const PSEO_KEYWORD_CATEGORIES = [
  "json",
  "password",
  "base64",
  "uuid",
  "color",
  "markdown",
  "pdf",
  "image",
  "text",
  "hash",
  "qr",
] as const;

const NON_DEFAULT_LOCALES = ["ar", "es", "fr", "de", "pt", "zh"] as const;

function programmaticRedirects() {
  const rules: { source: string; destination: string; permanent: boolean }[] =
    [];
  for (const cat of PSEO_KEYWORD_CATEGORIES) {
    rules.push({
      source: `/${cat}/:page`,
      destination: `/c/${cat}/:page`,
      permanent: true,
    });
    for (const locale of NON_DEFAULT_LOCALES) {
      rules.push({
        source: `/${locale}/${cat}/:page`,
        destination: `/${locale}/c/${cat}/:page`,
        permanent: true,
      });
    }
  }
  return rules;
}

const nextConfig: NextConfig = {
  output: "standalone",
  reactStrictMode: true,
  poweredByHeader: false,
  images: {
    formats: ["image/avif", "image/webp"],
  },
  experimental: {
    optimizePackageImports: ["lucide-react", "framer-motion"],
  },
  async redirects() {
    return programmaticRedirects();
  },
  async headers() {
    return [
      {
        source: "/sw.js",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=0, must-revalidate",
          },
          {
            key: "Service-Worker-Allowed",
            value: "/",
          },
        ],
      },
      {
        source: "/manifest.webmanifest",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=86400, stale-while-revalidate=604800",
          },
          {
            key: "Content-Type",
            value: "application/manifest+json",
          },
        ],
      },
      {
        source: "/_next/static/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
      {
        source: "/favicon.svg",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=86400, stale-while-revalidate=604800",
          },
        ],
      },
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
        ],
      },
    ];
  },
};

export default withSentryConfig(withNextIntl(nextConfig), {
  silent: true,
  disableLogger: true,
  sourcemaps: {
    disable: !process.env.SENTRY_AUTH_TOKEN,
  },
});

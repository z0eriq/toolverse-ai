import { getAppUrl } from "@/lib/utils";
import { sitemapIndexXml } from "@/lib/sitemap-helpers";
import { toolsSitemapPageCount } from "@/lib/sitemap-data";

/**
 * Sitemap index for millions of URLs — points to static, blog, and sharded tool feeds.
 * Served at /sitemap.xml (takes precedence over app/sitemap.ts when both exist — we replace robots).
 */
export async function GET() {
  const base = getAppUrl();
  const pages = await toolsSitemapPageCount();
  const toolSitemaps = Array.from({ length: pages }, (_, i) => `${base}/sitemap/tools/${i}`);
  const locs = [
    `${base}/sitemap/static`,
    `${base}/sitemap/blog`,
    `${base}/sitemap/tools`,
    ...toolSitemaps,
    `${base}/sitemap/programmatic`,
  ];

  return new Response(sitemapIndexXml(locs), {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
    },
  });
}

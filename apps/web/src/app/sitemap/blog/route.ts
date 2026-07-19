import { buildBlogSitemapEntries } from "@/lib/sitemap-data";
import { sitemapXml } from "@/lib/sitemap-helpers";

export async function GET() {
  const entries = await buildBlogSitemapEntries();
  return new Response(sitemapXml(entries), {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
    },
  });
}

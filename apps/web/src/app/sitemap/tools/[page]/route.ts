import { sitemapXml } from "@/lib/sitemap-helpers";
import { buildToolsSitemapPage } from "@/lib/sitemap-data";

export async function GET(
  _request: Request,
  context: { params: Promise<{ page: string }> },
) {
  const { page: pageRaw } = await context.params;
  const page = Math.max(0, Number.parseInt(pageRaw, 10) || 0);
  const entries = await buildToolsSitemapPage(page);
  return new Response(sitemapXml(entries), {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
    },
  });
}

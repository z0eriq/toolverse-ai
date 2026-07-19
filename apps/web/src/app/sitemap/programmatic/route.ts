import { api } from "@/lib/api";
import {
  localizedSitemapEntry,
  programmaticPublicPath,
  sitemapXml,
} from "@/lib/sitemap-helpers";

export async function GET() {
  let entries: { path: string; page_type: string; updated_at: string }[] = [];
  try {
    entries = await api.programmaticSitemap();
  } catch {
    entries = [];
  }

  const sitemap = entries.flatMap((entry) =>
    localizedSitemapEntry({
      path: programmaticPublicPath(entry.path),
      lastModified: entry.updated_at,
      changeFrequency: "weekly",
      priority:
        entry.page_type === "best_of"
          ? 0.8
          : entry.page_type === "use_case" ||
              entry.page_type === "industry" ||
              entry.page_type === "comparison"
            ? 0.75
            : 0.7,
    }),
  );

  return new Response(sitemapXml(sitemap), {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
    },
  });
}

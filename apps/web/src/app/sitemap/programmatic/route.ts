import { api } from "@/lib/api";
import { localizedSitemapEntry, sitemapXml } from "@/lib/sitemap-helpers";

const KEYWORD_CATEGORIES = new Set([
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
]);

/** Map API programmatic path to the public Next.js route. */
export function programmaticPublicPath(apiPath: string): string {
  const path = apiPath.replace(/^\/+/, "");
  if (path.startsWith("best/")) return `/${path}`;
  if (path.startsWith("tools/for-")) return `/${path}`;
  if (path.startsWith("hub/")) return `/${path}`;
  if (path.startsWith("use/")) {
    return `/use-cases/${path.slice("use/".length)}`;
  }
  if (path.startsWith("industry/")) {
    return `/industries/${path.slice("industry/".length)}`;
  }
  if (path.startsWith("compare/")) return `/${path}`;
  const [category, ...rest] = path.split("/");
  if (category && rest.length > 0 && KEYWORD_CATEGORIES.has(category)) {
    return `/c/${category}/${rest.join("/")}`;
  }
  return `/${path}`;
}

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

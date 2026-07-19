import type { MetadataRoute } from "next";
import { getAppUrl } from "@/lib/utils";
import { locales, type AppLocale } from "@/i18n/routing";

export type SitemapChangeFrequency =
  NonNullable<MetadataRoute.Sitemap[number]["changeFrequency"]>;

function localePath(locale: AppLocale, path: string): string {
  const base = getAppUrl();
  const normalized =
    path === "/" ? "" : path.startsWith("/") ? path : `/${path}`;
  if (locale === "en") {
    return `${base}${normalized || ""}`;
  }
  return `${base}/${locale}${normalized || ""}`;
}

function languageAlternates(path: string): Record<string, string> {
  const languages: Record<string, string> = {};
  for (const locale of locales) {
    languages[locale] = localePath(locale, path);
  }
  languages["x-default"] = localePath("en", path);
  return languages;
}

/** Build URLs for all locales with hreflang-style language alternates. */
export function localizedSitemapEntry(input: {
  path: string;
  lastModified?: Date | string;
  changeFrequency?: SitemapChangeFrequency;
  priority?: number;
}): MetadataRoute.Sitemap {
  const path =
    input.path === "/"
      ? "/"
      : input.path.startsWith("/")
        ? input.path
        : `/${input.path}`;
  const lastModified =
    typeof input.lastModified === "string"
      ? new Date(input.lastModified)
      : (input.lastModified ?? new Date());
  const changeFrequency = input.changeFrequency ?? "weekly";
  const priority = input.priority ?? 0.7;
  const alternates = { languages: languageAlternates(path) };

  return locales.map((locale) => ({
    url: localePath(locale, path),
    lastModified,
    changeFrequency,
    priority,
    alternates,
  }));
}

export function escapeXml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export function sitemapXml(entries: MetadataRoute.Sitemap): string {
  const urls = entries
    .map((entry) => {
      const langs = entry.alternates?.languages
        ? Object.entries(entry.alternates.languages)
            .map(
              ([lang, href]) =>
                `    <xhtml:link rel="alternate" hreflang="${escapeXml(lang)}" href="${escapeXml(String(href))}" />`,
            )
            .join("\n")
        : "";
      return `  <url>
    <loc>${escapeXml(entry.url)}</loc>
    <lastmod>${new Date(entry.lastModified ?? new Date()).toISOString()}</lastmod>
    <changefreq>${entry.changeFrequency ?? "weekly"}</changefreq>
    <priority>${entry.priority ?? 0.5}</priority>
${langs}
  </url>`;
    })
    .join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
${urls}
</urlset>`;
}

export function sitemapIndexXml(locs: string[]): string {
  const now = new Date().toISOString();
  const body = locs
    .map(
      (loc) => `  <sitemap>
    <loc>${escapeXml(loc)}</loc>
    <lastmod>${now}</lastmod>
  </sitemap>`,
    )
    .join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${body}
</sitemapindex>`;
}

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

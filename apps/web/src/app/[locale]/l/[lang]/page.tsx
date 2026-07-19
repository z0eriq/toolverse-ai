import type { Metadata } from "next";
import { setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { routing } from "@/i18n/routing";
import { buildPageMetadata } from "@/lib/seo";
import { getAllTools } from "@/tools/registry";

const LANG_LABELS: Record<string, string> = {
  en: "English",
  ar: "العربية",
  es: "Español",
  fr: "Français",
  de: "Deutsch",
  pt: "Português",
  zh: "中文",
};

export const revalidate = 3600;

export async function generateStaticParams() {
  return routing.locales.flatMap((locale) =>
    routing.locales.map((lang) => ({ locale, lang })),
  );
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; lang: string }>;
}): Promise<Metadata> {
  const { locale, lang } = await params;
  const label = LANG_LABELS[lang] ?? lang;
  return buildPageMetadata({
    title: `ToolVerse AI — ${label}`,
    description: `Free online tools with ${label} interface and localized SEO.`,
    path: `/l/${lang}`,
    locale,
  });
}

export default async function LocaleHubPage({
  params,
}: {
  params: Promise<{ locale: string; lang: string }>;
}) {
  const { locale, lang } = await params;
  setRequestLocale(locale);
  const label = LANG_LABELS[lang] ?? lang;
  const tools = getAllTools().slice(0, 24);

  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-4xl font-semibold tracking-tight">
        ToolVerse AI — {label}
      </h1>
      <p className="mt-3 max-w-2xl text-[var(--muted)]">
        Browse free developer and productivity tools. Switch language anytime from
        the header.
      </p>
      <ul className="mt-6 flex flex-wrap gap-2 text-sm">
        {routing.locales.map((l) => (
          <li key={l}>
            <Link
              href={`/l/${l}`}
              locale={l}
              className={
                l === lang
                  ? "font-semibold text-[var(--accent)]"
                  : "text-[var(--muted)] hover:text-[var(--foreground)]"
              }
            >
              {LANG_LABELS[l] ?? l}
            </Link>
          </li>
        ))}
      </ul>
      <ul className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {tools.map((tool) => (
          <li key={tool.manifest.slug}>
            <Link
              href={`/tools/${tool.manifest.category}/${tool.manifest.slug}`}
              className="block surface rounded-[var(--radius-lg)] p-4 transition hover:border-[var(--accent)]"
            >
              <p className="font-medium">
                {typeof tool.manifest.name === "string"
                  ? tool.manifest.name
                  : tool.manifest.name?.en ?? tool.manifest.slug}
              </p>
              <p className="mt-1 font-mono text-xs text-[var(--muted)]">
                {tool.manifest.category}/{tool.manifest.slug}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

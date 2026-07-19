import { Link } from "@/i18n/navigation";
import { ToolCard } from "@/components/ToolCard";
import {
  breadcrumbJsonLd,
  jsonLdScript,
  websiteJsonLd,
} from "@/lib/seo";
import { localize } from "@/lib/utils";
import type { ProgrammaticPageDetail, ToolListItem } from "@/lib/api";

export interface RelatedToolCard {
  slug: string;
  category: string;
  name: Record<string, string> | string;
  description: Record<string, string> | string;
  premium?: boolean;
  toolId: string;
}

function resolveBodyHtml(
  body: ProgrammaticPageDetail["body"],
  locale: string,
): string {
  if (!body) return "";
  if (typeof body === "string") return body;
  const localized = localize(body as Record<string, string>, locale);
  if (localized) return localized;
  const en = typeof body.en === "string" ? body.en : "";
  if (en) return en;
  const first = Object.values(body).find((v) => typeof v === "string");
  return typeof first === "string" ? first : "";
}

export function ProgrammaticLanding({
  page,
  locale,
  publicPath,
  relatedTools,
  crumbs,
}: {
  page: ProgrammaticPageDetail;
  locale: string;
  /** Canonical path without locale prefix, e.g. /best/pdf-tools */
  publicPath: string;
  relatedTools: RelatedToolCard[];
  crumbs: { name: string; path: string }[];
}) {
  const title = localize(page.seo_title || page.title, locale) || localize(page.title, locale);
  const description =
    localize(page.seo_description || page.description, locale) ||
    localize(page.description, locale);
  const bodyHtml = resolveBodyHtml(page.body, locale);

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: jsonLdScript(websiteJsonLd(locale)) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: jsonLdScript(breadcrumbJsonLd(crumbs)),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: jsonLdScript({
            "@context": "https://schema.org",
            "@type": "WebPage",
            name: title,
            description,
            url: publicPath,
            inLanguage: locale,
          }),
        }}
      />

      <nav aria-label="Breadcrumb" className="mb-6 text-sm text-[var(--muted)]">
        <ol className="flex flex-wrap items-center gap-1.5">
          {crumbs.map((crumb, index) => (
            <li key={crumb.path} className="flex items-center gap-1.5">
              {index > 0 ? <span aria-hidden>/</span> : null}
              {index === crumbs.length - 1 ? (
                <span className="text-[var(--foreground)]">{crumb.name}</span>
              ) : (
                <Link href={crumb.path} className="hover:text-[var(--accent)]">
                  {crumb.name}
                </Link>
              )}
            </li>
          ))}
        </ol>
      </nav>

      <header className="max-w-3xl">
        {page.page_type ? (
          <p className="text-xs uppercase tracking-wider text-[var(--accent)]">
            {page.page_type.replace(/_/g, " ")}
          </p>
        ) : null}
        <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight sm:text-4xl">
          {title}
        </h1>
        {description ? (
          <p className="mt-4 text-lg text-[var(--muted)]">{description}</p>
        ) : null}
      </header>

      {bodyHtml ? (
        <div
          className="prose-muted mt-10 max-w-3xl space-y-4 text-[var(--foreground)] [&_a]:text-[var(--accent)] [&_p]:text-[var(--muted)]"
          dangerouslySetInnerHTML={{ __html: bodyHtml }}
        />
      ) : null}

      {relatedTools.length > 0 ? (
        <section className="mt-14">
          <h2 className="font-display text-xl font-semibold">
            {locale === "ar" ? "أدوات ذات صلة" : "Related tools"}
          </h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {relatedTools.map((tool, index) => (
              <ToolCard
                key={tool.toolId}
                slug={tool.slug}
                category={tool.category}
                name={tool.name}
                description={tool.description}
                locale={locale}
                premium={tool.premium}
                toolId={tool.toolId}
                index={index}
              />
            ))}
          </div>
        </section>
      ) : null}

      <section className="mt-14 surface rounded-[var(--radius-lg)] p-6">
        <h2 className="font-display text-lg font-semibold">
          {locale === "ar" ? "استكشف المزيد" : "Explore more"}
        </h2>
        <ul className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-sm">
          <li>
            <Link href="/best/pdf-tools" className="text-[var(--accent)] hover:underline">
              Best PDF tools
            </Link>
          </li>
          <li>
            <Link
              href="/tools/for-developers"
              className="text-[var(--accent)] hover:underline"
            >
              Tools for developers
            </Link>
          </li>
          <li>
            <Link href="/hub/developer" className="text-[var(--accent)] hover:underline">
              Developer hub
            </Link>
          </li>
          <li>
            <Link href="/#tools" className="text-[var(--accent)] hover:underline">
              All tools
            </Link>
          </li>
        </ul>
      </section>
    </div>
  );
}

export function toolListToCards(items: ToolListItem[]): RelatedToolCard[] {
  return items.map((item) => ({
    slug: item.slug,
    category: item.category,
    name: item.name,
    description: item.description,
    premium: item.premium,
    toolId: item.tool_id,
  }));
}

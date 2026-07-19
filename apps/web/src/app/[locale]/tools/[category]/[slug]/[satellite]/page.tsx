import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { setRequestLocale } from "next-intl/server";
import type { ToolManifest } from "@toolverse/tool-sdk";
import {
  breadcrumbJsonLd,
  faqJsonLd,
  howToJsonLd,
  jsonLdScript,
  softwareAppJsonLd,
} from "@/lib/seo";
import { api, type ToolDetail, type ToolListItem } from "@/lib/api";
import { getAllTools, getToolBySlug } from "@/tools/registry";
import { localize } from "@/lib/utils";
import { ShareBar } from "@/components/ShareBar";
import { ToolCard } from "@/components/ToolCard";
import { ToolSatelliteNav } from "@/components/ToolSatelliteNav";
import { Link } from "@/i18n/navigation";
import {
  SATELLITE_KINDS,
  buildSatelliteContent,
  buildToolSeoContext,
  isSatelliteKind,
  satelliteMetadata,
  satellitePath,
  type SatelliteKind,
} from "@/lib/tool-satellites";

export const dynamicParams = true;

export function generateStaticParams() {
  const tools = getAllTools();
  const params: { category: string; slug: string; satellite: string }[] = [];
  for (const tool of tools) {
    for (const satellite of SATELLITE_KINDS) {
      params.push({
        category: tool.manifest.category,
        slug: tool.manifest.slug,
        satellite,
      });
    }
  }
  return params;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; category: string; slug: string; satellite: string }>;
}): Promise<Metadata> {
  const { locale, category, slug, satellite } = await params;
  if (!isSatelliteKind(satellite)) return { title: "Not found" };
  const fs = getToolBySlug(slug);
  let apiTool: ToolDetail | null = null;
  try {
    apiTool = await api.tool(slug);
  } catch {
    apiTool = null;
  }
  const ctx = buildToolSeoContext(locale, fs?.manifest ?? null, apiTool, []);
  if (!ctx || ctx.category !== category) return { title: "Not found" };
  return satelliteMetadata(ctx, satellite, locale);
}

async function loadRelated(slug: string): Promise<ToolListItem[]> {
  try {
    return await api.relatedTools(slug, 6);
  } catch {
    return [];
  }
}

export default async function ToolSatellitePage({
  params,
}: {
  params: Promise<{ locale: string; category: string; slug: string; satellite: string }>;
}) {
  const { locale, category, slug, satellite } = await params;
  setRequestLocale(locale);
  if (!isSatelliteKind(satellite)) notFound();

  const fs = getToolBySlug(slug);
  let apiTool: ToolDetail | null = null;
  try {
    apiTool = await api.tool(slug);
  } catch {
    apiTool = null;
  }
  if (!fs && !apiTool) notFound();
  if ((apiTool?.category ?? fs?.manifest.category) !== category) notFound();

  const related = await loadRelated(slug);
  const ctx = buildToolSeoContext(locale, fs?.manifest ?? null, apiTool, related);
  if (!ctx) notFound();

  const content = buildSatelliteContent(ctx, satellite as SatelliteKind, locale);
  const path = satellitePath(category, slug, satellite as SatelliteKind);
  const schemas: unknown[] = [
    softwareAppJsonLd(
      (fs?.manifest ?? {
        id: ctx.toolId,
        slug: ctx.slug,
        category: ctx.category as ToolManifest["category"],
        name: { en: ctx.name },
        description: { en: ctx.description },
        version: ctx.version,
        seo: { title: { en: ctx.name }, keywords: [] },
        capabilities: ctx.capabilities as ToolManifest["capabilities"],
      }) as ToolManifest,
      locale,
    ),
    breadcrumbJsonLd([
      { name: "Home", path: "/" },
      { name: ctx.category, path: `/?category=${ctx.category}` },
      { name: ctx.name, path: `/tools/${category}/${slug}` },
      { name: content.title, path },
    ]),
  ];
  if (satellite === "faq" && ctx.faq.length) schemas.push(faqJsonLd(ctx.faq));
  if (satellite === "howto" && ctx.howto.length) {
    schemas.push(howToJsonLd(ctx.name, ctx.howto));
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      {schemas.map((schema, i) => (
        <script
          key={i}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: jsonLdScript(schema) }}
        />
      ))}

      <p className="text-xs uppercase tracking-wider text-[var(--accent)]">{ctx.category}</p>
      <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight sm:text-4xl">
        {content.title}
      </h1>
      <p className="mt-3 max-w-3xl text-[var(--muted)]">{content.intro}</p>
      <ShareBar className="mt-4" title={content.title} path={path} />

      <div className="mt-6">
        <ToolSatelliteNav
          category={category}
          slug={slug}
          locale={locale}
          active={satellite as SatelliteKind}
        />
      </div>

      <div className="mt-10 space-y-8">
        {content.sections.map((section) => (
          <section key={section.heading} className="surface rounded-[var(--radius-lg)] p-6">
            <h2 className="font-display text-xl font-semibold">{section.heading}</h2>
            <p className="mt-2 text-[var(--muted)]">{section.body}</p>
            {section.bullets?.length ? (
              <ul className="mt-3 list-disc space-y-1 ps-5 text-sm text-[var(--muted)]">
                {section.bullets.map((b) => (
                  <li key={b}>{b}</li>
                ))}
              </ul>
            ) : null}
            {section.code ? (
              <pre className="mt-4 overflow-x-auto rounded-lg bg-[var(--bg)] p-4 text-xs leading-relaxed">
                <code>{section.code}</code>
              </pre>
            ) : null}
          </section>
        ))}
      </div>

      <div className="mt-10">
        <Link
          href={`/tools/${category}/${slug}`}
          className="inline-flex h-10 items-center rounded-full bg-[var(--accent)] px-5 text-sm font-medium text-[var(--accent-fg)]"
        >
          {locale === "ar" ? `افتح ${ctx.name}` : `Open ${ctx.name}`}
        </Link>
      </div>

      {related.length > 0 ? (
        <section className="mt-16">
          <h2 className="font-display text-xl font-semibold">
            {locale === "ar" ? "أدوات ذات صلة" : "Related tools"}
          </h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {related.slice(0, 6).map((item, index) => (
              <ToolCard
                key={item.tool_id}
                slug={item.slug}
                category={item.category}
                name={item.name}
                description={item.description}
                locale={locale}
                premium={item.premium}
                index={index}
              />
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}

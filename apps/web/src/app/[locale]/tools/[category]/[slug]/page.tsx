import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getTranslations, setRequestLocale } from "next-intl/server";
import type { ToolManifest } from "@toolverse/tool-sdk";
import {
  breadcrumbJsonLd,
  faqJsonLd,
  howToJsonLd,
  jsonLdScript,
  softwareAppJsonLd,
  toolMetadata,
} from "@/lib/seo";
import { api, type ToolDetail, type ToolFaqItem, type ToolHowToStep, type ToolListItem } from "@/lib/api";
import { getToolBySlug, getToolsByCategory } from "@/tools/registry";
import { localize } from "@/lib/utils";
import { AdSlot } from "@/components/AdSlot";
import { AffiliateCta } from "@/components/AffiliateCta";
import { ShareBar } from "@/components/ShareBar";
import { SponsoredBadge } from "@/components/SponsoredBadge";
import { ToolCard } from "@/components/ToolCard";
import { FavoriteButton } from "@/components/FavoriteButton";
import { PremiumGate } from "@/components/PremiumGate";
import { DynamicToolRuntimeClient } from "@/components/DynamicToolRuntimeClient";
import { ToolSatelliteNav } from "@/components/ToolSatelliteNav";
import { ToolReviews } from "@/components/ToolReviews";
import { Link } from "@/i18n/navigation";
import { SATELLITE_KINDS, satelliteLabel } from "@/lib/tool-satellites";

export const dynamicParams = true;

export async function generateStaticParams() {
  const { getAllTools } = await import("@/tools/registry");
  return getAllTools().map((tool) => ({
    category: tool.manifest.category,
    slug: tool.manifest.slug,
  }));
}

async function fetchApiTool(slug: string): Promise<ToolDetail | null> {
  try {
    return await api.tool(slug);
  } catch {
    return null;
  }
}

async function fetchRelated(
  slug: string,
  category: string,
): Promise<
  {
    slug: string;
    category: string;
    name: Record<string, string> | string;
    description: Record<string, string> | string;
    premium?: boolean;
    toolId: string;
  }[]
> {
  try {
    const related = await api.relatedTools(slug, 3);
    if (related.length > 0) {
      return related.map((item: ToolListItem) => ({
        slug: item.slug,
        category: item.category,
        name: item.name,
        description: item.description,
        premium: item.premium,
        toolId: item.tool_id,
      }));
    }
  } catch {
    // fall through to filesystem
  }

  return getToolsByCategory(category)
    .filter((item) => item.manifest.slug !== slug)
    .slice(0, 3)
    .map((item) => ({
      slug: item.manifest.slug,
      category: item.manifest.category,
      name: item.manifest.name,
      description: item.manifest.description,
      premium: item.manifest.premium,
      toolId: item.manifest.id,
    }));
}

function resolveFaqs(
  apiTool: ToolDetail | null,
  manifest: ToolManifest | null,
): ToolFaqItem[] {
  if (apiTool?.faq && Array.isArray(apiTool.faq) && apiTool.faq.length > 0) {
    return apiTool.faq.filter((f) => f?.question && f?.answer);
  }
  const fromManifest = manifest?.faq;
  if (fromManifest && fromManifest.length > 0) return fromManifest;
  return [];
}

function resolveHowTo(
  apiTool: ToolDetail | null,
  manifest: ToolManifest | null,
): ToolHowToStep[] {
  if (
    apiTool?.howto_steps &&
    Array.isArray(apiTool.howto_steps) &&
    apiTool.howto_steps.length > 0
  ) {
    return apiTool.howto_steps.filter((s) => s?.name && s?.text);
  }
  const fromManifest = manifest?.howto_steps ?? manifest?.howto;
  if (fromManifest && fromManifest.length > 0) return fromManifest;
  return [];
}

function manifestFromApi(apiTool: ToolDetail): ToolManifest {
  const name =
    typeof apiTool.name === "string"
      ? { en: apiTool.name }
      : (apiTool.name as ToolManifest["name"]);
  const description =
    typeof apiTool.description === "string"
      ? { en: apiTool.description }
      : (apiTool.description as ToolManifest["description"]);
  const seoTitle =
    typeof apiTool.seo_title === "string"
      ? { en: apiTool.seo_title }
      : (apiTool.seo_title as ToolManifest["seo"]["title"] | undefined) ?? name;
  const seoDescription =
    typeof apiTool.seo_description === "string"
      ? { en: apiTool.seo_description }
      : (apiTool.seo_description as ToolManifest["seo"]["description"] | undefined) ??
        description;

  return {
    id: apiTool.tool_id,
    slug: apiTool.slug,
    category: apiTool.category as ToolManifest["category"],
    name,
    description,
    version: apiTool.version,
    premium: apiTool.premium,
    adsenseSlot: (apiTool.adsense_slot as ToolManifest["adsenseSlot"]) ?? "sidebar",
    capabilities: (apiTool.capabilities as ToolManifest["capabilities"]) ?? ["server"],
    icon: apiTool.icon,
    order: apiTool.order,
    schemaType: (apiTool.schema_type as ToolManifest["schemaType"]) ?? "WebApplication",
    seo: {
      title: seoTitle,
      description: seoDescription,
      keywords: apiTool.seo_keywords ?? [],
    },
    faq: apiTool.faq,
    howto_steps: apiTool.howto_steps,
  };
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; category: string; slug: string }>;
}): Promise<Metadata> {
  const { locale, category, slug } = await params;
  const fsTool = getToolBySlug(slug);
  if (fsTool && fsTool.manifest.category === category) {
    return toolMetadata(fsTool.manifest, locale);
  }

  const apiTool = await fetchApiTool(slug);
  if (apiTool && apiTool.category === category) {
    const manifest = manifestFromApi(apiTool);
    return toolMetadata(manifest, locale);
  }

  return { title: "Tool not found" };
}

export default async function ToolPage({
  params,
}: {
  params: Promise<{ locale: string; category: string; slug: string }>;
}) {
  const { locale, category, slug } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("tool");

  const fsTool = getToolBySlug(slug);
  const apiTool = await fetchApiTool(slug);

  const isDynamic = apiTool?.source === "dynamic";
  const hasFsMatch = Boolean(fsTool && fsTool.manifest.category === category);
  const hasApiMatch = Boolean(apiTool && apiTool.category === category);

  if (!hasFsMatch && !hasApiMatch) notFound();
  if (hasApiMatch && apiTool && apiTool.category !== category) notFound();
  if (hasFsMatch && fsTool && fsTool.manifest.category !== category && !hasApiMatch) {
    notFound();
  }

  let manifest: ToolManifest;
  if (isDynamic && apiTool) {
    manifest = manifestFromApi(apiTool);
  } else if (fsTool?.manifest) {
    manifest = fsTool.manifest;
  } else if (apiTool) {
    manifest = manifestFromApi(apiTool);
  } else {
    notFound();
  }

  if (manifest.category !== category) notFound();

  const FsComponent = fsTool?.Component;
  const name = localize(manifest.name, locale);
  const description = localize(manifest.description, locale);
  const related = await fetchRelated(slug, manifest.category);
  const faqs = resolveFaqs(apiTool, fsTool?.manifest ?? null);
  const howto = resolveHowTo(apiTool, fsTool?.manifest ?? null);
  const toolId = apiTool?.tool_id ?? manifest.id;
  const useDynamicRuntime = isDynamic || !FsComponent;

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: jsonLdScript(softwareAppJsonLd(manifest, locale)),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: jsonLdScript(
            breadcrumbJsonLd([
              { name: "Home", path: "/" },
              { name: manifest.category, path: `/?category=${manifest.category}` },
              { name, path: `/tools/${manifest.category}/${manifest.slug}` },
            ]),
          ),
        }}
      />
      {faqs.length > 0 ? (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: jsonLdScript(faqJsonLd(faqs)) }}
        />
      ) : null}
      {howto.length > 0 ? (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: jsonLdScript(howToJsonLd(name, howto)),
          }}
        />
      ) : null}

      <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-3xl">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-xs uppercase tracking-wider text-[var(--accent)]">
              {manifest.category}
            </p>
            <SponsoredBadge toolId={toolId} toolSlug={manifest.slug} />
          </div>
          <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight sm:text-4xl">
            {name}
          </h1>
          <p className="mt-3 text-[var(--muted)]">{description}</p>
          <ShareBar
            className="mt-4"
            title={name}
            path={`/tools/${manifest.category}/${manifest.slug}`}
          />
        </div>
        <FavoriteButton toolId={toolId} />
      </div>

      <div className="mb-8">
        <ToolSatelliteNav
          category={manifest.category}
          slug={manifest.slug}
          locale={locale}
          active="main"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
        <div>
          <PremiumGate premium={Boolean(manifest.premium)}>
            {useDynamicRuntime || !FsComponent ? (
              <DynamicToolRuntimeClient
                slug={slug}
                toolId={toolId}
                uiSchema={apiTool?.ui_schema}
                capabilities={manifest.capabilities}
              />
            ) : (
              <FsComponent />
            )}
          </PremiumGate>
        </div>
        <div className="space-y-4">
          <AdSlot
            slot={
              manifest.adsenseSlot === "in-tool"
                ? "in-tool"
                : manifest.adsenseSlot === "none"
                  ? "banner"
                  : "sidebar"
            }
          />
          <AffiliateCta toolId={toolId} toolSlug={manifest.slug} />
        </div>
      </div>

      {faqs.length > 0 ? (
        <section className="mt-16">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <h2 className="font-display text-xl font-semibold">{t("faq")}</h2>
            <Link
              href={`/tools/${manifest.category}/${manifest.slug}/faq`}
              className="text-sm text-[var(--accent)] hover:underline"
            >
              {satelliteLabel("faq", locale)} →
            </Link>
          </div>
          <dl className="mt-4 space-y-4">
            {faqs.map((item) => (
              <div
                key={item.question}
                className="surface rounded-[var(--radius-lg)] p-4"
              >
                <dt className="font-medium">{item.question}</dt>
                <dd className="mt-2 text-sm text-[var(--muted)]">{item.answer}</dd>
              </div>
            ))}
          </dl>
        </section>
      ) : null}

      <ToolReviews toolId={toolId} toolSlug={manifest.slug} />

      <section className="mt-12 surface rounded-[var(--radius-lg)] p-6">
        <h2 className="font-display text-lg font-semibold">
          {locale === "ar" ? "أدلة SEO" : "Guides & docs"}
        </h2>
        <ul className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3 text-sm">
          {SATELLITE_KINDS.map((kind) => (
            <li key={kind}>
              <Link
                href={`/tools/${manifest.category}/${manifest.slug}/${kind}`}
                className="text-[var(--accent)] hover:underline"
              >
                {satelliteLabel(kind, locale)}
              </Link>
            </li>
          ))}
        </ul>
      </section>

      {related.length > 0 ? (
        <section className="mt-16">
          <h2 className="font-display text-xl font-semibold">{t("related")}</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {related.map((item, index) => (
              <ToolCard
                key={item.toolId}
                slug={item.slug}
                category={item.category}
                name={item.name}
                description={item.description}
                locale={locale}
                premium={item.premium}
                toolId={item.toolId}
                index={index}
              />
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}

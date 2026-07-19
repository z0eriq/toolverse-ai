import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { buildPageMetadata, jsonLdScript, websiteJsonLd } from "@/lib/seo";
import { Button } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";
import { CategoryGrid } from "@/components/CategoryGrid";
import { ToolCard } from "@/components/ToolCard";
import { AdSlot } from "@/components/AdSlot";
import { HomeSearch } from "@/features/search/home-search";
import { getFeaturedTools } from "@/tools/registry";
import { HeroVisual } from "@/components/HeroVisual";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "home" });
  return buildPageMetadata({
    title: "ToolVerse AI",
    description: t("supporting"),
    path: "/",
    locale,
  });
}

export default async function HomePage({
  params,
  searchParams,
}: {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{ category?: string; q?: string }>;
}) {
  const { locale } = await params;
  const { category } = await searchParams;
  setRequestLocale(locale);
  const t = await getTranslations("home");
  const featured = getFeaturedTools(6);

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: jsonLdScript(websiteJsonLd(locale)) }}
      />
      <section className="relative overflow-hidden">
        <div className="bg-mesh absolute inset-0 -z-10 opacity-80" aria-hidden />
        <div className="mx-auto grid max-w-6xl items-center gap-10 px-4 pb-16 pt-14 sm:px-6 lg:grid-cols-[1.1fr_0.9fr] lg:gap-12 lg:pb-24 lg:pt-20">
          <div>
            <p className="font-display text-sm font-semibold uppercase tracking-[0.2em] text-[var(--accent)]">
              {t("brand")}
            </p>
            <h1 className="mt-4 font-display text-4xl font-semibold tracking-tight text-balance sm:text-5xl lg:text-6xl">
              {t("headline")}
            </h1>
            <p className="mt-5 max-w-xl text-base text-[var(--muted)] sm:text-lg">
              {t("supporting")}
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="lg">
                <Link href="/#tools">{t("browseTools")}</Link>
              </Button>
              <Button asChild size="lg" variant="secondary">
                <Link href="/auth/register">{t("getStarted")}</Link>
              </Button>
            </div>
          </div>
          <HeroVisual />
        </div>
      </section>

      <div className="mx-auto max-w-6xl space-y-20 px-4 pb-20 sm:px-6">
        <HomeSearch initialCategory={category} />

        <section>
          <div className="mb-6 max-w-2xl">
            <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
              {t("categoriesHeading")}
            </h2>
            <p className="mt-2 text-[var(--muted)]">{t("categoriesSupporting")}</p>
          </div>
          <CategoryGrid locale={locale} />
        </section>

        <section>
          <div className="mb-6 max-w-2xl">
            <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
              {t("featuredHeading")}
            </h2>
            <p className="mt-2 text-[var(--muted)]">{t("featuredSupporting")}</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {featured.map((tool, index) => (
              <ToolCard
                key={tool.manifest.id}
                slug={tool.manifest.slug}
                category={tool.manifest.category}
                name={tool.manifest.name}
                description={tool.manifest.description}
                locale={locale}
                premium={tool.manifest.premium}
                index={index}
              />
            ))}
          </div>
        </section>

        <AdSlot slot="banner" />
      </div>
    </>
  );
}

import type { Metadata } from "next";
import type { LocalizedString, ToolManifest } from "@toolverse/tool-sdk";
import { LOCALE_OG_MAP, locales, type AppLocale } from "@/i18n/routing";
import { getAppUrl, getSiteName, localize } from "./utils";

export function absoluteUrl(path = "/"): string {
  const base = getAppUrl();
  if (!path || path === "/") return base;
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

function localeAbsoluteUrl(locale: string, path = "/"): string {
  const normalized =
    !path || path === "/" ? "" : path.startsWith("/") ? path : `/${path}`;
  if (locale === "en" || !locale) {
    return absoluteUrl(normalized || "/");
  }
  return absoluteUrl(`/${locale}${normalized}`);
}

function languageAlternates(path = "/"): Record<string, string> {
  const languages: Record<string, string> = {};
  for (const locale of locales) {
    languages[locale] = localeAbsoluteUrl(locale, path);
  }
  return languages;
}

export function buildPageMetadata(input: {
  title: string;
  description: string;
  path?: string;
  locale?: string;
  keywords?: string[];
  image?: string;
  noIndex?: boolean;
}): Metadata {
  const site = getSiteName();
  const path = input.path ?? "/";
  const url = localeAbsoluteUrl(input.locale ?? "en", path);
  const image = input.image ?? absoluteUrl("/api/og");
  const title = input.title.includes(site) ? input.title : `${input.title} | ${site}`;
  const ogLocale =
    LOCALE_OG_MAP[(input.locale as AppLocale) ?? "en"] ?? "en_US";

  return {
    title,
    description: input.description,
    keywords: input.keywords,
    alternates: {
      canonical: url,
      languages: languageAlternates(path),
    },
    openGraph: {
      title,
      description: input.description,
      url,
      siteName: site,
      locale: ogLocale,
      type: "website",
      images: [{ url: image, width: 1200, height: 630, alt: title }],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description: input.description,
      images: [image],
    },
    robots: input.noIndex
      ? { index: false, follow: false }
      : { index: true, follow: true },
  };
}

export function toolMetadata(manifest: ToolManifest, locale: string): Metadata {
  const title = localize(manifest.seo.title, locale);
  const description = localize(
    manifest.seo.description ?? manifest.description,
    locale,
  );
  return buildPageMetadata({
    title,
    description,
    path: `/tools/${manifest.category}/${manifest.slug}`,
    locale,
    keywords: manifest.seo.keywords,
    image: absoluteUrl(
      `/api/og?title=${encodeURIComponent(title)}&subtitle=${encodeURIComponent(description)}`,
    ),
  });
}

export function websiteJsonLd(locale: string) {
  const site = getSiteName();
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: site,
    url: absoluteUrl("/"),
    inLanguage: locale,
    potentialAction: {
      "@type": "SearchAction",
      target: `${absoluteUrl("/")}?q={search_term_string}`,
      "query-input": "required name=search_term_string",
    },
  };
}

export function organizationJsonLd() {
  const site = getSiteName();
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: site,
    url: absoluteUrl("/"),
    logo: absoluteUrl("/api/og"),
    sameAs: [] as string[],
  };
}

export function faqJsonLd(faqs: { question: string; answer: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  };
}

export function howToJsonLd(
  name: string,
  steps: { name: string; text: string }[],
) {
  return {
    "@context": "https://schema.org",
    "@type": "HowTo",
    name,
    step: steps.map((step, index) => ({
      "@type": "HowToStep",
      position: index + 1,
      name: step.name,
      text: step.text,
    })),
  };
}

export function softwareAppJsonLd(
  manifest: ToolManifest,
  locale: string,
  extras?: {
    offers?: { price: string; priceCurrency: string };
    aggregateRating?: {
      ratingValue: number;
      ratingCount: number;
      bestRating?: number;
      worstRating?: number;
    };
  },
) {
  const name = localize(manifest.name, locale);
  const description = localize(manifest.description, locale);
  const offers = extras?.offers ?? {
    price: manifest.premium ? "9.00" : "0",
    priceCurrency: "USD",
  };

  return {
    "@context": "https://schema.org",
    "@type": manifest.schemaType ?? "WebApplication",
    name,
    description,
    applicationCategory: "UtilitiesApplication",
    operatingSystem: "Web",
    url: absoluteUrl(`/tools/${manifest.category}/${manifest.slug}`),
    offers: {
      "@type": "Offer",
      price: offers.price,
      priceCurrency: offers.priceCurrency,
    },
    ...(extras?.aggregateRating
      ? {
          aggregateRating: {
            "@type": "AggregateRating",
            ratingValue: extras.aggregateRating.ratingValue,
            ratingCount: extras.aggregateRating.ratingCount,
            bestRating: extras.aggregateRating.bestRating ?? 5,
            worstRating: extras.aggregateRating.worstRating ?? 1,
          },
        }
      : {}),
  };
}

export function breadcrumbJsonLd(
  items: { name: string; path: string }[],
) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: absoluteUrl(item.path),
    })),
  };
}

export function articleJsonLd(input: {
  title: string;
  description: string;
  slug: string;
  publishedAt?: string | null;
  authorName?: string;
}) {
  return {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: input.title,
    description: input.description,
    datePublished: input.publishedAt ?? undefined,
    author: input.authorName
      ? { "@type": "Person", name: input.authorName }
      : undefined,
    mainEntityOfPage: absoluteUrl(`/blog/${input.slug}`),
  };
}

export function jsonLdScript(data: unknown): string {
  return JSON.stringify(data).replace(/</g, "\\u003c");
}

export function localizedField(
  value: LocalizedString | Record<string, string> | string | undefined,
  locale: string,
): string {
  return localize(value as LocalizedString | string | undefined, locale);
}

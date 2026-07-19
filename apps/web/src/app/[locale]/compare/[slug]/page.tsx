import type { Metadata } from "next";
import { setRequestLocale } from "next-intl/server";
import {
  fetchProgrammaticPage,
  programmaticMetadata,
  renderProgrammaticPage,
} from "@/lib/programmatic";
import { localize } from "@/lib/utils";

export const dynamicParams = true;
export const revalidate = 3600;

/** Public route maps to API slug `compare/{slug}`. */
function apiPath(slug: string) {
  return `compare/${slug}`;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { locale, slug } = await params;
  const path = apiPath(slug);
  const page = await fetchProgrammaticPage(path);
  if (!page) return { title: "Not found" };
  return programmaticMetadata(page, locale, `/compare/${slug}`);
}

export default async function ComparePage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  setRequestLocale(locale);
  const path = apiPath(slug);
  const page = await fetchProgrammaticPage(path);
  const title = page
    ? localize(page.title, locale)
    : slug.replace(/-/g, " ");

  return renderProgrammaticPage({
    path,
    publicPath: `/compare/${slug}`,
    locale,
    crumbs: [
      { name: "Home", path: "/" },
      { name: "Compare", path: "/compare" },
      { name: title, path: `/compare/${slug}` },
    ],
  });
}

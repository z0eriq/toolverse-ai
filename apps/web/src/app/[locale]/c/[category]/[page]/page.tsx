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

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; category: string; page: string }>;
}): Promise<Metadata> {
  const { locale, category, page: pageSlug } = await params;
  const path = `${category}/${pageSlug}`;
  const page = await fetchProgrammaticPage(path);
  if (!page) return { title: "Not found" };
  return programmaticMetadata(page, locale, `/c/${category}/${pageSlug}`);
}

export default async function CategoryKeywordPage({
  params,
}: {
  params: Promise<{ locale: string; category: string; page: string }>;
}) {
  const { locale, category, page: pageSlug } = await params;
  setRequestLocale(locale);
  const path = `${category}/${pageSlug}`;
  const page = await fetchProgrammaticPage(path);
  const title = page
    ? localize(page.title, locale)
    : pageSlug.replace(/-/g, " ");

  return renderProgrammaticPage({
    path,
    publicPath: `/c/${category}/${pageSlug}`,
    locale,
    crumbs: [
      { name: "Home", path: "/" },
      { name: category, path: `/hub/${category}` },
      { name: title, path: `/c/${category}/${pageSlug}` },
    ],
  });
}

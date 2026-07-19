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
  params: Promise<{ locale: string; category: string }>;
}): Promise<Metadata> {
  const { locale, category } = await params;
  const path = `hub/${category}`;
  const page = await fetchProgrammaticPage(path);
  if (!page) return { title: "Not found" };
  return programmaticMetadata(page, locale, `/hub/${category}`);
}

export default async function CategoryHubPage({
  params,
}: {
  params: Promise<{ locale: string; category: string }>;
}) {
  const { locale, category } = await params;
  setRequestLocale(locale);
  const path = `hub/${category}`;
  const page = await fetchProgrammaticPage(path);
  const title = page
    ? localize(page.title, locale)
    : `${category} tools`;

  return renderProgrammaticPage({
    path,
    publicPath: `/hub/${category}`,
    locale,
    crumbs: [
      { name: "Home", path: "/" },
      { name: "Hubs", path: "/hub/developer" },
      { name: title, path: `/hub/${category}` },
    ],
  });
}

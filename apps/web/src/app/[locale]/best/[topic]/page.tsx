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
  params: Promise<{ locale: string; topic: string }>;
}): Promise<Metadata> {
  const { locale, topic } = await params;
  const path = `best/${topic}`;
  const page = await fetchProgrammaticPage(path);
  if (!page) return { title: "Not found" };
  return programmaticMetadata(page, locale, `/best/${topic}`);
}

export default async function BestTopicPage({
  params,
}: {
  params: Promise<{ locale: string; topic: string }>;
}) {
  const { locale, topic } = await params;
  setRequestLocale(locale);
  const path = `best/${topic}`;
  const page = await fetchProgrammaticPage(path);
  const title = page
    ? localize(page.title, locale)
    : topic.replace(/-/g, " ");

  return renderProgrammaticPage({
    path,
    publicPath: `/best/${topic}`,
    locale,
    crumbs: [
      { name: "Home", path: "/" },
      { name: "Best", path: "/best/pdf-tools" },
      { name: title, path: `/best/${topic}` },
    ],
  });
}

import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { setRequestLocale } from "next-intl/server";
import {
  fetchProgrammaticPage,
  programmaticMetadata,
  renderProgrammaticPage,
} from "@/lib/programmatic";
import { localize } from "@/lib/utils";

export const dynamicParams = true;
export const revalidate = 3600;

/** Single-segment routes under /tools/* that are audience hubs (for-*). */
function isAudienceSegment(segment: string): boolean {
  return segment.startsWith("for-") && segment.length > 4;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; segment: string }>;
}): Promise<Metadata> {
  const { locale, segment } = await params;
  if (!isAudienceSegment(segment)) return { title: "Not found" };
  const path = `tools/${segment}`;
  const page = await fetchProgrammaticPage(path);
  if (!page) return { title: "Not found" };
  return programmaticMetadata(page, locale, `/tools/${segment}`);
}

export default async function ToolsAudiencePage({
  params,
}: {
  params: Promise<{ locale: string; segment: string }>;
}) {
  const { locale, segment } = await params;
  setRequestLocale(locale);
  if (!isAudienceSegment(segment)) notFound();

  const path = `tools/${segment}`;
  const page = await fetchProgrammaticPage(path);
  const title = page
    ? localize(page.title, locale)
    : segment.replace(/^for-/, "").replace(/-/g, " ");

  return renderProgrammaticPage({
    path,
    publicPath: `/tools/${segment}`,
    locale,
    crumbs: [
      { name: "Home", path: "/" },
      { name: "Tools", path: "/#tools" },
      { name: title, path: `/tools/${segment}` },
    ],
  });
}

import { notFound } from "next/navigation";
import type { Metadata } from "next";
import {
  api,
  type ProgrammaticPageDetail,
  type ToolListItem,
} from "@/lib/api";
import { buildPageMetadata } from "@/lib/seo";
import { localize } from "@/lib/utils";
import { getToolBySlug } from "@/tools/registry";
import {
  ProgrammaticLanding,
  toolListToCards,
  type RelatedToolCard,
} from "@/components/ProgrammaticLanding";

export async function fetchProgrammaticPage(
  path: string,
): Promise<ProgrammaticPageDetail | null> {
  try {
    return await api.programmaticByPath(path);
  } catch {
    return null;
  }
}

export async function resolveRelatedTools(
  toolIds: string[],
): Promise<RelatedToolCard[]> {
  const cards: RelatedToolCard[] = [];
  for (const id of toolIds.slice(0, 9)) {
    const fs = getToolBySlug(id);
    if (fs) {
      cards.push({
        slug: fs.manifest.slug,
        category: fs.manifest.category,
        name: fs.manifest.name,
        description: fs.manifest.description,
        premium: fs.manifest.premium,
        toolId: fs.manifest.id,
      });
      continue;
    }
    try {
      const tool = await api.tool(id);
      cards.push(...toolListToCards([tool as ToolListItem]));
    } catch {
      // skip missing tools
    }
  }
  return cards;
}

export function programmaticMetadata(
  page: ProgrammaticPageDetail,
  locale: string,
  publicPath: string,
): Metadata {
  const title =
    localize(page.seo_title || page.title, locale) || localize(page.title, locale);
  const description =
    localize(page.seo_description || page.description, locale) ||
    localize(page.description, locale);
  return buildPageMetadata({
    title,
    description,
    path: publicPath,
    locale,
    keywords: page.seo_keywords?.length
      ? page.seo_keywords
      : page.keyword
        ? [page.keyword]
        : undefined,
  });
}

export async function renderProgrammaticPage(input: {
  path: string;
  publicPath: string;
  locale: string;
  crumbs: { name: string; path: string }[];
}) {
  const page = await fetchProgrammaticPage(input.path);
  if (!page) notFound();
  const relatedTools = await resolveRelatedTools(page.related_tool_ids ?? []);
  return (
    <ProgrammaticLanding
      page={page}
      locale={input.locale}
      publicPath={input.publicPath}
      relatedTools={relatedTools}
      crumbs={input.crumbs}
    />
  );
}

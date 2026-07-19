import type { MetadataRoute } from "next";
import { api, type BlogPostListItem } from "@/lib/api";
import { AUTHORITY_PAGE_SLUGS } from "@/lib/authority-pages";
import { getAllTools } from "@/tools/registry";
import { localizedSitemapEntry } from "@/lib/sitemap-helpers";
import { SATELLITE_KINDS, allToolSeoPaths } from "@/lib/tool-satellites";
import { listLocalPosts } from "@/content/blog";

/** Max URL entries per sitemap shard (before locale doubling). */
export const TOOLS_SITEMAP_PAGE_SIZE = 500;

export interface ToolSitemapRow {
  slug: string;
  category: string;
  updated_at: string;
}

export async function loadToolSitemapRows(): Promise<ToolSitemapRow[]> {
  const now = new Date().toISOString();
  let apiTools: ToolSitemapRow[] = [];
  try {
    apiTools = await api.sitemapTools();
  } catch {
    apiTools = [];
  }
  if (apiTools.length === 0) {
    apiTools = getAllTools().map((t) => ({
      slug: t.manifest.slug,
      category: t.manifest.category,
      updated_at: now,
    }));
  }
  return apiTools;
}

/** Main tool pages + 7 satellite SEO pages per tool. */
export function buildToolSeoSitemapEntries(
  tools: ToolSitemapRow[],
): MetadataRoute.Sitemap {
  return tools.flatMap((tool) =>
    allToolSeoPaths(tool.category, tool.slug).flatMap((path, index) =>
      localizedSitemapEntry({
        path,
        lastModified: tool.updated_at,
        changeFrequency: "weekly",
        priority: index === 0 ? 0.85 : 0.65,
      }),
    ),
  );
}

export async function buildToolsSitemapEntries(): Promise<MetadataRoute.Sitemap> {
  const tools = await loadToolSitemapRows();
  return buildToolSeoSitemapEntries(tools);
}

export async function buildToolsSitemapPage(
  page: number,
): Promise<MetadataRoute.Sitemap> {
  const tools = await loadToolSitemapRows();
  // Each tool expands to 8 paths × N locales; shard by tool count
  const start = page * TOOLS_SITEMAP_PAGE_SIZE;
  const slice = tools.slice(start, start + TOOLS_SITEMAP_PAGE_SIZE);
  return buildToolSeoSitemapEntries(slice);
}

export async function toolsSitemapPageCount(): Promise<number> {
  const tools = await loadToolSitemapRows();
  return Math.max(1, Math.ceil(tools.length / TOOLS_SITEMAP_PAGE_SIZE));
}

async function loadPosts(): Promise<BlogPostListItem[]> {
  const local: BlogPostListItem[] = listLocalPosts().map((post) => ({
    slug: post.slug,
    title: post.title,
    excerpt: post.excerpt,
    cover_image: "",
    published_at: post.published_at,
    tags: [{ slug: post.category, name: post.category }],
    author_name: post.author_name,
    seo_title: post.seo_title,
    seo_description: post.seo_description,
  }));
  try {
    const data = await api.blogPosts();
    const remote = Array.isArray(data)
      ? data
      : data && typeof data === "object" && "results" in data
        ? data.results
        : [];
    const bySlug = new Map<string, BlogPostListItem>();
    for (const post of local) bySlug.set(post.slug, post);
    for (const post of remote) bySlug.set(post.slug, post);
    return Array.from(bySlug.values());
  } catch {
    return local;
  }
}

export async function buildBlogSitemapEntries(): Promise<MetadataRoute.Sitemap> {
  const posts = await loadPosts();
  const index = localizedSitemapEntry({
    path: "/blog",
    changeFrequency: "daily",
    priority: 0.7,
  });

  const postEntries = posts.flatMap((post) =>
    localizedSitemapEntry({
      path: `/blog/${post.slug}`,
      lastModified: post.published_at ?? undefined,
      changeFrequency: "monthly",
      priority: 0.6,
    }),
  );

  return [...index, ...postEntries];
}

const STATIC_PATHS: {
  path: string;
  changeFrequency: "daily" | "weekly" | "monthly";
  priority: number;
}[] = [
  { path: "/", changeFrequency: "daily", priority: 1 },
  { path: "/about", changeFrequency: "monthly", priority: 0.7 },
  { path: "/contact", changeFrequency: "monthly", priority: 0.65 },
  { path: "/privacy", changeFrequency: "monthly", priority: 0.6 },
  { path: "/terms", changeFrequency: "monthly", priority: 0.6 },
  { path: "/editorial-policy", changeFrequency: "monthly", priority: 0.55 },
  { path: "/blog", changeFrequency: "daily", priority: 0.75 },
  { path: "/pricing", changeFrequency: "weekly", priority: 0.7 },
  { path: "/developers", changeFrequency: "weekly", priority: 0.65 },
  { path: "/enterprise", changeFrequency: "weekly", priority: 0.7 },
  { path: "/community", changeFrequency: "weekly", priority: 0.65 },
  { path: "/best", changeFrequency: "weekly", priority: 0.75 },
  ...(["en", "ar", "es", "fr", "de", "pt", "zh"] as const).map((lang) => ({
    path: `/l/${lang}`,
    changeFrequency: "weekly" as const,
    priority: 0.75,
  })),
  { path: "/tools/for-developers", changeFrequency: "weekly", priority: 0.75 },
  { path: "/tools/for-students", changeFrequency: "weekly", priority: 0.75 },
  { path: "/tools/for-marketers", changeFrequency: "weekly", priority: 0.75 },
  ...AUTHORITY_PAGE_SLUGS.map((slug) => ({
    path: `/${slug}`,
    changeFrequency: "weekly" as const,
    priority: 0.8,
  })),
  { path: "/auth/login", changeFrequency: "monthly", priority: 0.4 },
  { path: "/auth/register", changeFrequency: "monthly", priority: 0.4 },
];

export function buildStaticSitemapEntries(): MetadataRoute.Sitemap {
  return STATIC_PATHS.flatMap((item) =>
    localizedSitemapEntry({
      path: item.path,
      changeFrequency: item.changeFrequency,
      priority: item.priority,
    }),
  );
}

export { SATELLITE_KINDS };

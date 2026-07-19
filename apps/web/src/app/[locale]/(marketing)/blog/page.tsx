import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { buildPageMetadata } from "@/lib/seo";
import { api, type BlogPostListItem } from "@/lib/api";
import { listLocalPosts } from "@/content/blog";
import { Link } from "@/i18n/navigation";
import { Card } from "@/components/ui/card";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "blog" });
  return buildPageMetadata({
    title: t("title"),
    description: t("supporting"),
    path: "/blog",
    locale,
  });
}

function localAsListItems(): BlogPostListItem[] {
  return listLocalPosts().map((post) => ({
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
}

async function loadPosts(): Promise<BlogPostListItem[]> {
  const local = localAsListItems();
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
    return Array.from(bySlug.values()).sort((a, b) =>
      String(b.published_at ?? "").localeCompare(String(a.published_at ?? "")),
    );
  } catch {
    return local;
  }
}

export default async function BlogPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("blog");
  const posts = await loadPosts();

  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <div className="max-w-2xl">
        <h1 className="font-display text-4xl font-semibold tracking-tight">
          {t("title")}
        </h1>
        <p className="mt-3 text-[var(--muted)]">{t("supporting")}</p>
      </div>
      {posts.length === 0 ? (
        <p className="mt-12 text-[var(--muted)]">{t("empty")}</p>
      ) : (
        <div className="mt-10 grid gap-4 md:grid-cols-2">
          {posts.map((post) => (
            <Card key={post.slug}>
              <Link href={`/blog/${post.slug}`} className="block">
                <h2 className="font-display text-xl font-semibold tracking-tight hover:text-[var(--accent)]">
                  {post.title}
                </h2>
                <p className="mt-2 line-clamp-3 text-sm text-[var(--muted)]">
                  {post.excerpt}
                </p>
                <span className="mt-4 inline-block text-sm text-[var(--accent)]">
                  {t("readMore")} →
                </span>
              </Link>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { buildPageMetadata } from "@/lib/seo";
import { api, type BlogPostListItem } from "@/lib/api";
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

async function loadPosts(): Promise<BlogPostListItem[]> {
  try {
    const data = await api.blogPosts();
    if (Array.isArray(data)) return data;
    if (data && typeof data === "object" && "results" in data) {
      return data.results;
    }
    return [];
  } catch {
    return [];
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
        <h1 className="font-display text-4xl font-semibold tracking-tight">{t("title")}</h1>
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
                <p className="mt-2 line-clamp-3 text-sm text-[var(--muted)]">{post.excerpt}</p>
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

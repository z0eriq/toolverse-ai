import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { setRequestLocale } from "next-intl/server";
import {
  articleJsonLd,
  buildPageMetadata,
  jsonLdScript,
} from "@/lib/seo";
import { api } from "@/lib/api";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { locale, slug } = await params;
  try {
    const post = await api.blogPost(slug);
    return buildPageMetadata({
      title: post.seo_title || post.title,
      description: post.seo_description || post.excerpt,
      path: `/blog/${slug}`,
      locale,
    });
  } catch {
    return buildPageMetadata({
      title: "Blog",
      description: "ToolVerse AI blog",
      path: `/blog/${slug}`,
      locale,
      noIndex: true,
    });
  }
}

export default async function BlogPostPage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  setRequestLocale(locale);

  let post;
  try {
    post = await api.blogPost(slug);
  } catch {
    notFound();
  }

  return (
    <article className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: jsonLdScript(
            articleJsonLd({
              title: post.title,
              description: post.excerpt,
              slug: post.slug,
              publishedAt: post.published_at,
              authorName: post.author_name,
            }),
          ),
        }}
      />
      <p className="text-sm text-[var(--muted)]">
        {post.published_at
          ? new Date(post.published_at).toLocaleDateString(locale)
          : null}
        {post.author_name ? ` · ${post.author_name}` : null}
      </p>
      <h1 className="mt-3 font-display text-4xl font-semibold tracking-tight">{post.title}</h1>
      <p className="mt-4 text-lg text-[var(--muted)]">{post.excerpt}</p>
      <div className="prose-tool mt-10 whitespace-pre-wrap text-base leading-relaxed">
        {post.content}
      </div>
    </article>
  );
}

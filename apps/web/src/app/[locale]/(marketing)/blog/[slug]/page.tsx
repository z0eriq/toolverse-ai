import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { setRequestLocale } from "next-intl/server";
import {
  articleJsonLd,
  buildPageMetadata,
  jsonLdScript,
} from "@/lib/seo";
import { api } from "@/lib/api";
import { getLocalPost } from "@/content/blog";
import { Link } from "@/i18n/navigation";

type ResolvedPost = {
  slug: string;
  title: string;
  excerpt: string;
  content: string;
  seo_title?: string;
  seo_description?: string;
  published_at?: string | null;
  author_name?: string;
  category?: string;
};

async function resolvePost(slug: string): Promise<ResolvedPost | null> {
  const local = getLocalPost(slug);
  if (local) {
    return {
      slug: local.slug,
      title: local.title,
      excerpt: local.excerpt,
      content: local.content,
      seo_title: local.seo_title,
      seo_description: local.seo_description,
      published_at: local.published_at,
      author_name: local.author_name,
      category: local.category,
    };
  }
  try {
    const post = await api.blogPost(slug);
    return {
      slug: post.slug,
      title: post.title,
      excerpt: post.excerpt,
      content: post.content,
      seo_title: post.seo_title,
      seo_description: post.seo_description,
      published_at: post.published_at,
      author_name: post.author_name,
    };
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { locale, slug } = await params;
  const post = await resolvePost(slug);
  if (!post) {
    return buildPageMetadata({
      title: "Blog",
      description: "ToolVerse AI blog",
      path: `/blog/${slug}`,
      locale,
      noIndex: true,
    });
  }
  return buildPageMetadata({
    title: post.seo_title || post.title,
    description: post.seo_description || post.excerpt,
    path: `/blog/${slug}`,
    locale,
  });
}

function renderArticleBody(content: string) {
  const blocks = content.split(/\n\n+/).map((b) => b.trim()).filter(Boolean);
  return blocks.map((block, index) => {
    if (block.startsWith("## ")) {
      return (
        <h2
          key={index}
          className="mt-10 font-display text-2xl font-semibold tracking-tight"
        >
          {block.replace(/^##\s+/, "")}
        </h2>
      );
    }
    if (block.startsWith("### ")) {
      return (
        <h3 key={index} className="mt-8 text-xl font-semibold">
          {block.replace(/^###\s+/, "")}
        </h3>
      );
    }
    if (block.startsWith("- ")) {
      const items = block.split("\n").filter((line) => line.startsWith("- "));
      return (
        <ul
          key={index}
          className="mt-4 list-disc space-y-2 ps-5 text-base leading-relaxed text-[var(--muted)]"
        >
          {items.map((item) => (
            <li key={item}>{item.replace(/^-\s+/, "")}</li>
          ))}
        </ul>
      );
    }
    return (
      <p key={index} className="mt-4 text-base leading-relaxed text-[var(--muted)]">
        {block}
      </p>
    );
  });
}

export default async function BlogPostPage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  setRequestLocale(locale);

  const post = await resolvePost(slug);
  if (!post) notFound();

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
        <Link href="/blog" className="text-[var(--accent)] hover:underline">
          Blog
        </Link>
        {post.category ? ` · ${post.category}` : null}
        {post.published_at
          ? ` · ${new Date(post.published_at).toLocaleDateString(locale)}`
          : null}
        {post.author_name ? ` · ${post.author_name}` : null}
      </p>
      <h1 className="mt-3 font-display text-4xl font-semibold tracking-tight">
        {post.title}
      </h1>
      <p className="mt-4 text-lg text-[var(--muted)]">{post.excerpt}</p>
      <div className="prose-tool mt-10">{renderArticleBody(post.content)}</div>
    </article>
  );
}

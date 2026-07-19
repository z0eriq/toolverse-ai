import { setRequestLocale } from "next-intl/server";
import {
  fetchProgrammaticPage,
  programmaticMetadata,
  renderProgrammaticPage,
} from "@/lib/programmatic";
import { localize } from "@/lib/utils";
import type { AuthorityPageSlug } from "@/lib/authority-pages";

export async function authorityGenerateMetadata(
  locale: string,
  slug: AuthorityPageSlug,
) {
  const page = await fetchProgrammaticPage(slug);
  if (!page) return { title: "Not found" };
  return programmaticMetadata(page, locale, `/${slug}`);
}

export async function AuthorityProgrammaticPage({
  locale,
  slug,
}: {
  locale: string;
  slug: AuthorityPageSlug;
}) {
  setRequestLocale(locale);
  const page = await fetchProgrammaticPage(slug);
  const title = page
    ? localize(page.title, locale)
    : slug.replace(/-/g, " ");

  return renderProgrammaticPage({
    path: slug,
    publicPath: `/${slug}`,
    locale,
    crumbs: [
      { name: "Home", path: "/" },
      { name: title, path: `/${slug}` },
    ],
  });
}

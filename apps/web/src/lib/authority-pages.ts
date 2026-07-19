/** Public authority paths keyed by ProgrammaticPage.slug / path_key. */
export const AUTHORITY_PAGE_SLUGS = [
  "best-ai-tools",
  "free-tools-for-students",
  "tools-for-developers",
  "productivity-tools",
] as const;

export type AuthorityPageSlug = (typeof AUTHORITY_PAGE_SLUGS)[number];

export function isAuthoritySlug(slug: string): slug is AuthorityPageSlug {
  return (AUTHORITY_PAGE_SLUGS as readonly string[]).includes(slug);
}

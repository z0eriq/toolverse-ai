"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Link } from "@/i18n/navigation";

function asList<T>(data: T[] | { results: T[] } | undefined): T[] {
  if (!data) return [];
  return Array.isArray(data) ? data : data.results;
}

export function CommunityPageClient() {
  const collections = useQuery({
    queryKey: ["community-collections"],
    queryFn: () => api.community.collections(),
    retry: false,
  });

  const list = asList(collections.data);

  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-4xl font-semibold tracking-tight">Community</h1>
      <p className="mt-3 max-w-2xl text-[var(--muted)]">
        Public collections curated by ToolVerse users.
      </p>
      <ul className="mt-10 grid gap-4 sm:grid-cols-2">
        {list.map((c) => (
          <li key={c.public_slug} className="surface rounded-[var(--radius-lg)] p-5">
            <Link
              href={`/collections/${c.public_slug}`}
              className="font-display text-lg font-semibold hover:text-[var(--accent)]"
            >
              {c.name}
            </Link>
            <p className="mt-2 text-sm text-[var(--muted)]">{c.description}</p>
            {c.owner_username ? (
              <Link
                href={`/u/${c.owner_username}`}
                className="mt-3 inline-block text-xs text-[var(--accent)] hover:underline"
              >
                @{c.owner_username}
              </Link>
            ) : null}
          </li>
        ))}
      </ul>
      {list.length === 0 && !collections.isLoading ? (
        <p className="mt-8 text-sm text-[var(--muted)]">
          No public collections yet. Publish one from your workspace.
        </p>
      ) : null}
    </div>
  );
}

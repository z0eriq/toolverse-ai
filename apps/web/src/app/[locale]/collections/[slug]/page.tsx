"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Link } from "@/i18n/navigation";
import { Card } from "@/components/ui/card";

export default function PublicCollectionPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const collection = useQuery({
    queryKey: ["community-collection", slug],
    queryFn: () => api.community.collection(slug),
    retry: false,
  });

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <Link href="/community" className="text-sm text-[var(--accent)] hover:underline">
        ← Community
      </Link>
      {collection.isError ? (
        <p className="mt-6 text-[var(--color-danger)]" role="alert">
          Collection not found.
        </p>
      ) : null}
      {collection.data ? (
        <>
          <h1 className="mt-4 font-display text-3xl font-semibold">
            {collection.data.name}
          </h1>
          <p className="mt-2 text-[var(--muted)]">{collection.data.description}</p>
          {collection.data.owner_username ? (
            <Link
              href={`/u/${collection.data.owner_username}`}
              className="mt-3 inline-block text-sm text-[var(--accent)] hover:underline"
            >
              @{collection.data.owner_username}
            </Link>
          ) : null}
          <ul className="mt-8 space-y-2">
            {(collection.data.items ?? []).map((item, idx) => (
              <li key={idx}>
                <Card className="text-sm">
                  {item.title || item.tool_slug || "Item"}
                </Card>
              </li>
            ))}
          </ul>
        </>
      ) : collection.isLoading ? (
        <p className="mt-6 text-sm text-[var(--muted)]">Loading…</p>
      ) : null}
    </div>
  );
}

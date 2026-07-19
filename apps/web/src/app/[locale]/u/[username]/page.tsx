"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Link } from "@/i18n/navigation";
import { Card } from "@/components/ui/card";

export default function PublicProfilePage({
  params,
}: {
  params: Promise<{ username: string }>;
}) {
  const { username } = use(params);
  const profile = useQuery({
    queryKey: ["community-profile", username],
    queryFn: () => api.community.profile(username),
    retry: false,
  });

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <Link href="/community" className="text-sm text-[var(--accent)] hover:underline">
        ← Community
      </Link>
      {profile.isError ? (
        <p className="mt-6 text-[var(--color-danger)]" role="alert">
          Profile not found or not public.
        </p>
      ) : null}
      {profile.data ? (
        <>
          <h1 className="mt-4 font-display text-4xl font-semibold">
            @{profile.data.username}
          </h1>
          {profile.data.headline ? (
            <p className="mt-2 text-lg text-[var(--muted)]">{profile.data.headline}</p>
          ) : null}
          {profile.data.bio ? (
            <p className="mt-4 text-sm text-[var(--muted)]">{profile.data.bio}</p>
          ) : null}
          <section className="mt-10">
            <h2 className="font-display text-xl font-semibold">Collections</h2>
            <ul className="mt-4 space-y-3">
              {(profile.data.collections ?? []).map((c) => (
                <li key={c.public_slug}>
                  <Card>
                    <Link
                      href={`/collections/${c.public_slug}`}
                      className="font-medium hover:text-[var(--accent)]"
                    >
                      {c.name}
                    </Link>
                  </Card>
                </li>
              ))}
            </ul>
          </section>
        </>
      ) : profile.isLoading ? (
        <p className="mt-6 text-sm text-[var(--muted)]">Loading…</p>
      ) : null}
    </div>
  );
}

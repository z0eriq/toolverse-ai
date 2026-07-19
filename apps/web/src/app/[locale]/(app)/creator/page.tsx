"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/features/auth/auth-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link } from "@/i18n/navigation";

function asList<T>(data: T[] | { results: T[] } | undefined): T[] {
  if (!data) return [];
  return Array.isArray(data) ? data : data.results;
}

export default function CreatorPortalPage() {
  const { user, isLoading } = useAuth();
  const queryClient = useQueryClient();
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [toolSlug, setToolSlug] = useState("");
  const [toolName, setToolName] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const profile = useQuery({
    queryKey: ["creator-profile"],
    queryFn: () => api.creator.profile(),
    enabled: Boolean(user),
    retry: false,
  });

  const submissions = useQuery({
    queryKey: ["creator-submissions"],
    queryFn: () => api.creator.submissions(),
    enabled: Boolean(user),
    retry: false,
  });

  const saveProfile = useMutation({
    mutationFn: () =>
      api.creator.updateProfile({
        display_name: displayName || profile.data?.display_name,
        bio: bio || profile.data?.bio,
      }),
    onSuccess: async () => {
      setMessage("Profile saved.");
      await queryClient.invalidateQueries({ queryKey: ["creator-profile"] });
    },
  });

  const createSub = useMutation({
    mutationFn: async () => {
      const created = await api.creator.createSubmission({
        type: "tool",
        payload: {
          slug: toolSlug.trim(),
          name: { en: toolName.trim() },
          category_slug: "ai",
          recipe: "generic",
        },
      });
      return api.creator.submitForReview(created.id);
    },
    onSuccess: async () => {
      setMessage("Submitted for review.");
      setToolSlug("");
      setToolName("");
      await queryClient.invalidateQueries({ queryKey: ["creator-submissions"] });
    },
    onError: (err) => {
      setMessage(err instanceof ApiError ? err.message : "Submit failed");
    },
  });

  if (isLoading) return <div className="p-8">…</div>;

  if (!user) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h1 className="font-display text-3xl font-semibold">Creator hub</h1>
        <p className="mt-2 text-[var(--muted)]">
          Sign in to submit tools and templates for review.
        </p>
        <Button asChild className="mt-6">
          <Link href="/auth/login">Log in</Link>
        </Button>
      </div>
    );
  }

  const list = asList(submissions.data);

  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-3xl font-semibold tracking-tight">
        Creator hub
      </h1>
      <p className="mt-2 max-w-2xl text-[var(--muted)]">
        Submit tools or templates for approval. Revenue-share stubs track accrued
        payouts when enabled.
      </p>

      {message ? (
        <p className="mt-4 text-sm text-[var(--muted)]" role="status">
          {message}
        </p>
      ) : null}

      <div className="mt-10 grid gap-8 lg:grid-cols-2">
        <Card>
          <h2 className="font-display text-lg font-semibold">Creator profile</h2>
          <form
            className="mt-4 space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              saveProfile.mutate();
            }}
          >
            <div>
              <Label htmlFor="c-name">Display name</Label>
              <Input
                id="c-name"
                value={displayName || profile.data?.display_name || ""}
                onChange={(e) => setDisplayName(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="c-bio">Bio</Label>
              <textarea
                id="c-bio"
                className="mt-1 min-h-[80px] w-full rounded-[var(--radius-md)] border border-[var(--border)] bg-transparent p-3 text-sm"
                value={bio || profile.data?.bio || ""}
                onChange={(e) => setBio(e.target.value)}
              />
            </div>
            <Button type="submit" disabled={saveProfile.isPending}>
              Save profile
            </Button>
          </form>
        </Card>

        <Card>
          <h2 className="font-display text-lg font-semibold">Submit a tool</h2>
          <form
            className="mt-4 space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              createSub.mutate();
            }}
          >
            <div>
              <Label htmlFor="c-slug">Slug</Label>
              <Input
                id="c-slug"
                value={toolSlug}
                onChange={(e) => setToolSlug(e.target.value)}
                required
                pattern="[a-z0-9-]+"
              />
            </div>
            <div>
              <Label htmlFor="c-tool-name">Name</Label>
              <Input
                id="c-tool-name"
                value={toolName}
                onChange={(e) => setToolName(e.target.value)}
                required
              />
            </div>
            <Button type="submit" disabled={createSub.isPending}>
              Submit for review
            </Button>
          </form>
        </Card>
      </div>

      <section className="mt-12">
        <h2 className="font-display text-xl font-semibold">Your submissions</h2>
        <ul className="mt-4 space-y-3">
          {list.map((s) => (
            <li key={s.id} className="surface rounded-[var(--radius-lg)] p-4 text-sm">
              <p className="font-medium">
                #{s.id} · {s.type} · {s.status}
              </p>
              {s.tool_spec_slug ? (
                <p className="mt-1 font-mono text-xs text-[var(--muted)]">
                  tool_spec: {s.tool_spec_slug}
                </p>
              ) : null}
            </li>
          ))}
        </ul>
        {list.length === 0 ? (
          <p className="mt-4 text-sm text-[var(--muted)]">No submissions yet.</p>
        ) : null}
      </section>
    </div>
  );
}

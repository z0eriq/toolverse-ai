"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Link } from "@/i18n/navigation";

export default function SharedWorkflowPage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = use(params);
  const shared = useQuery({
    queryKey: ["workflow-shared", token],
    queryFn: () => api.workflows.shared(token),
    retry: false,
  });

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <Link href="/workflows" className="text-sm text-[var(--accent)] hover:underline">
        ← Workflows
      </Link>
      <h1 className="mt-4 font-display text-3xl font-semibold">Shared workflow</h1>
      {shared.isError ? (
        <p className="mt-4 text-[var(--color-danger)]" role="alert">
          Workflow not found or not shareable.
        </p>
      ) : null}
      {shared.data ? (
        <Card className="mt-6">
          <p className="font-display text-xl font-semibold">{shared.data.name}</p>
          <p className="mt-2 font-mono text-xs text-[var(--muted)]">
            {shared.data.slug} · {shared.data.visibility}
          </p>
          <pre className="mt-4 overflow-x-auto text-xs text-[var(--muted)]">
            {JSON.stringify(shared.data.steps, null, 2)}
          </pre>
        </Card>
      ) : shared.isLoading ? (
        <p className="mt-4 text-sm text-[var(--muted)]">Loading…</p>
      ) : null}
    </div>
  );
}

"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, api, type WorkflowTemplateItem } from "@/lib/api";
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

export default function WorkflowsPage() {
  const { user, isLoading } = useAuth();
  const queryClient = useQueryClient();
  const [name, setName] = useState("My workflow");
  const [stepSlug, setStepSlug] = useState("json-formatter");
  const [inputText, setInputText] = useState('{"hello":"world"}');
  const [runOutput, setRunOutput] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const templates = useQuery({
    queryKey: ["workflow-templates"],
    queryFn: () => api.workflows.templates(),
    retry: false,
  });

  const workflows = useQuery({
    queryKey: ["my-workflows"],
    queryFn: () => api.workflows.list(),
    enabled: Boolean(user),
    retry: false,
  });

  const createMutation = useMutation({
    mutationFn: () =>
      api.workflows.create({
        name: name.trim(),
        visibility: "private",
        steps: [
          { type: "tool", tool_slug: stepSlug.trim() || "json-formatter" },
          {
            type: "transform",
            op: "trim",
            source: "output",
            target: "output",
          },
        ],
      }),
    onSuccess: async () => {
      setError(null);
      await queryClient.invalidateQueries({ queryKey: ["my-workflows"] });
    },
    onError: (err) => {
      setError(err instanceof ApiError ? err.message : "Could not create workflow");
    },
  });

  const runMutation = useMutation({
    mutationFn: (id: number) => {
      let parsed: Record<string, unknown> = { input: inputText };
      try {
        parsed = { input: JSON.parse(inputText) };
      } catch {
        parsed = { input: inputText };
      }
      return api.workflows.run(id, parsed);
    },
    onSuccess: (result) => {
      setRunOutput(
        JSON.stringify(result.output ?? result.output_payload ?? result, null, 2),
      );
      setError(null);
    },
    onError: (err) => {
      setError(err instanceof ApiError ? err.message : "Run failed");
    },
  });

  const list = asList(workflows.data);
  const tplList = asList(templates.data);

  const shareBase = useMemo(() => {
    if (typeof window === "undefined") return "";
    return window.location.origin;
  }, []);

  if (isLoading) return <div className="p-8">…</div>;

  if (!user) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h1 className="font-display text-3xl font-semibold">Workflows</h1>
        <p className="mt-2 text-[var(--muted)]">
          Sign in to chain tools into reusable pipelines.
        </p>
        <Button asChild className="mt-6">
          <Link href="/auth/login">Log in</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-3xl font-semibold tracking-tight">
        Workflow builder
      </h1>
      <p className="mt-2 max-w-2xl text-[var(--muted)]">
        Chain tools into pipelines, save them, share with a token, and track runs.
      </p>

      <div className="mt-10 grid gap-8 lg:grid-cols-2">
        <Card>
          <h2 className="font-display text-lg font-semibold">Create workflow</h2>
          <form
            className="mt-4 space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              createMutation.mutate();
            }}
          >
            <div>
              <Label htmlFor="wf-name">Name</Label>
              <Input
                id="wf-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div>
              <Label htmlFor="wf-step">First tool slug</Label>
              <Input
                id="wf-step"
                value={stepSlug}
                onChange={(e) => setStepSlug(e.target.value)}
                required
              />
            </div>
            <Button type="submit" disabled={createMutation.isPending}>
              Save workflow
            </Button>
          </form>
          {error ? (
            <p className="mt-3 text-sm text-[var(--color-danger)]" role="alert">
              {error}
            </p>
          ) : null}
        </Card>

        <Card>
          <h2 className="font-display text-lg font-semibold">Templates</h2>
          <ul className="mt-4 space-y-2 text-sm">
            {tplList.map((tpl: WorkflowTemplateItem) => (
              <li key={tpl.id} className="rounded-[var(--radius-md)] border border-[var(--border)] p-3">
                <p className="font-medium">{tpl.name}</p>
                <p className="mt-1 text-xs text-[var(--muted)]">{tpl.description}</p>
              </li>
            ))}
          </ul>
          {tplList.length === 0 ? (
            <p className="mt-3 text-sm text-[var(--muted)]">No public templates yet.</p>
          ) : null}
        </Card>
      </div>

      <section className="mt-12">
        <h2 className="font-display text-xl font-semibold">Your workflows</h2>
        <ul className="mt-4 space-y-4">
          {list.map((wf) => (
            <li key={wf.id} className="surface rounded-[var(--radius-lg)] p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-medium">{wf.name}</p>
                  <p className="mt-1 font-mono text-xs text-[var(--muted)]">
                    {wf.slug} · {wf.visibility} · {wf.steps?.length ?? 0} steps
                  </p>
                  <p className="mt-2 text-xs text-[var(--muted)] break-all">
                    Share: {shareBase}/workflows/shared/{wf.share_token}
                  </p>
                </div>
                <Button
                  type="button"
                  size="sm"
                  disabled={runMutation.isPending}
                  onClick={() => runMutation.mutate(wf.id)}
                >
                  Run
                </Button>
              </div>
            </li>
          ))}
        </ul>
        {list.length === 0 ? (
          <p className="mt-4 text-sm text-[var(--muted)]">No workflows yet.</p>
        ) : null}
      </section>

      <Card className="mt-8">
        <Label htmlFor="wf-input">Run input</Label>
        <textarea
          id="wf-input"
          className="mt-2 min-h-[100px] w-full rounded-[var(--radius-md)] border border-[var(--border)] bg-transparent p-3 font-mono text-sm"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        />
        {runOutput ? (
          <pre className="mt-4 overflow-x-auto rounded-[var(--radius-md)] border border-[var(--border)] p-3 text-xs">
            {runOutput}
          </pre>
        ) : null}
      </Card>
    </div>
  );
}

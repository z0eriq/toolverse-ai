"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { ApiError, api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link } from "@/i18n/navigation";

function asList<T>(data: T[] | { results: T[] } | undefined): T[] {
  if (!data) return [];
  return Array.isArray(data) ? data : data.results;
}

export function AdminSeoHealthSection() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();
  const [path, setPath] = useState("/");

  const health = useQuery({
    queryKey: ["admin-seo-health"],
    queryFn: () => api.seoHealth.list(),
    retry: false,
  });

  const analyze = useMutation({
    mutationFn: () => api.seoHealth.analyze(path.trim()),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-seo-health"] });
    },
  });

  const recompute = useMutation({
    mutationFn: () => api.seoHealth.recompute(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-seo-health"] });
    },
  });

  const list = asList(health.data);

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h3 className="font-display text-lg font-semibold">{t("seoHealthTitle")}</h3>
          <p className="mt-1 text-sm text-[var(--muted)]">{t("seoHealthSupporting")}</p>
        </div>
        <Button
          type="button"
          size="sm"
          variant="secondary"
          disabled={recompute.isPending}
          onClick={() => recompute.mutate()}
        >
          {t("seoHealthRecompute")}
        </Button>
      </div>
      <form
        className="flex flex-wrap items-end gap-3"
        onSubmit={(e) => {
          e.preventDefault();
          analyze.mutate();
        }}
      >
        <div className="min-w-[240px] flex-1">
          <Label htmlFor="health-path">{t("seoAnalyzePath")}</Label>
          <Input
            id="health-path"
            value={path}
            onChange={(e) => setPath(e.target.value)}
            required
          />
        </div>
        <Button type="submit" disabled={analyze.isPending}>
          {t("seoHealthAnalyze")}
        </Button>
      </form>
      <ul className="divide-y divide-[var(--border)] overflow-hidden rounded-[var(--radius-lg)] surface">
        {list.map((row) => (
          <li
            key={row.id}
            className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm"
          >
            <span className="font-mono text-xs">{row.path}</span>
            <span className="tabular-nums font-semibold">
              {Number(row.overall).toFixed(0)}
            </span>
          </li>
        ))}
      </ul>
      {list.length === 0 && !health.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("seoHealthEmpty")}</p>
      ) : null}
    </section>
  );
}

export function AdminGrowthAgentPanel() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();

  const insights = useQuery({
    queryKey: ["admin-growth-insights"],
    queryFn: () => api.growthAgent.insights(),
    retry: false,
  });

  const actions = useQuery({
    queryKey: ["admin-growth-actions"],
    queryFn: () => api.growthAgent.listActions({ status: "proposed" }),
    retry: false,
  });

  const runMutation = useMutation({
    mutationFn: () => api.growthAgent.startRun(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-growth-insights"] });
      await queryClient.invalidateQueries({ queryKey: ["admin-growth-actions"] });
    },
  });

  const accept = useMutation({
    mutationFn: (id: number) => api.growthAgent.acceptInsight(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-growth-insights"] });
    },
  });

  const dismiss = useMutation({
    mutationFn: (id: number) => api.growthAgent.dismissInsight(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-growth-insights"] });
    },
  });

  const approveAction = useMutation({
    mutationFn: (id: number) => api.growthAgent.approveAction(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-growth-actions"] });
    },
  });

  const rejectAction = useMutation({
    mutationFn: (id: number) => api.growthAgent.rejectAction(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-growth-actions"] });
    },
  });

  const list = asList(insights.data);
  const actionList = asList(actions.data);

  return (
    <div className="mt-8 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="font-display text-xl font-semibold">{t("growthAgentTitle")}</h2>
          <p className="mt-1 text-sm text-[var(--muted)]">{t("growthAgentSupporting")}</p>
        </div>
        <Button
          type="button"
          disabled={runMutation.isPending}
          onClick={() => runMutation.mutate()}
        >
          {runMutation.isPending ? t("growthAgentRunning") : t("growthAgentRun")}
        </Button>
      </div>
      {runMutation.isError ? (
        <p className="text-sm text-[var(--color-danger)]" role="alert">
          {runMutation.error instanceof ApiError
            ? runMutation.error.message
            : t("growthAgentError")}
        </p>
      ) : null}

      <section className="space-y-3">
        <h3 className="font-display text-lg font-semibold">
          {t("growthAgentActionsTitle")}
        </h3>
        <p className="text-sm text-[var(--muted)]">
          {t("growthAgentActionsSupporting")}
        </p>
        <ul className="space-y-3">
          {actionList.map((action) => (
            <li
              key={action.id}
              className="surface rounded-[var(--radius-lg)] p-4 text-sm"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-medium">{action.action_type}</p>
                  <p className="mt-1 text-xs text-[var(--muted)]">
                    #{action.id} · {action.status}
                  </p>
                  <pre className="mt-2 max-h-24 overflow-auto text-xs text-[var(--muted)]">
                    {JSON.stringify(action.payload, null, 2)}
                  </pre>
                </div>
                {action.status === "proposed" ? (
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      size="sm"
                      disabled={approveAction.isPending}
                      onClick={() => approveAction.mutate(action.id)}
                    >
                      {t("growthAgentApproveAction")}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      disabled={rejectAction.isPending}
                      onClick={() => rejectAction.mutate(action.id)}
                    >
                      {t("growthAgentRejectAction")}
                    </Button>
                  </div>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
        {actionList.length === 0 && !actions.isLoading ? (
          <p className="text-sm text-[var(--muted)]">
            {t("growthAgentActionsEmpty")}
          </p>
        ) : null}
      </section>

      <section className="space-y-3">
        <h3 className="font-display text-lg font-semibold">
          {t("growthAgentInsightsTitle")}
        </h3>
        <ul className="space-y-3">
          {list.map((insight) => (
            <li key={insight.id} className="surface rounded-[var(--radius-lg)] p-4 text-sm">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-medium">
                    [{insight.category}] {insight.title}
                  </p>
                  <p className="mt-1 text-xs text-[var(--muted)]">
                    priority {insight.priority} · {insight.status}
                  </p>
                  <p className="mt-2 text-[var(--muted)]">{insight.rationale}</p>
                </div>
                {insight.status === "open" ? (
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      size="sm"
                      onClick={() => accept.mutate(insight.id)}
                    >
                      {t("growthAgentAccept")}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      onClick={() => dismiss.mutate(insight.id)}
                    >
                      {t("growthAgentDismiss")}
                    </Button>
                  </div>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
        {list.length === 0 && !insights.isLoading ? (
          <p className="text-sm text-[var(--muted)]">{t("growthAgentEmpty")}</p>
        ) : null}
      </section>
    </div>
  );
}

export function AdminWorkflowsPanel() {
  const t = useTranslations("admin");

  const templates = useQuery({
    queryKey: ["admin-workflow-templates"],
    queryFn: () => api.workflows.adminTemplates(),
    retry: false,
  });

  const list = asList(templates.data);

  return (
    <div className="mt-8 space-y-4">
      <h2 className="font-display text-xl font-semibold">{t("workflowsAdminTitle")}</h2>
      <p className="text-sm text-[var(--muted)]">{t("workflowsAdminSupporting")}</p>
      <p className="text-sm">
        <Link href="/workflows" className="text-[var(--accent)] hover:underline">
          {t("workflowsOpenApp")}
        </Link>
      </p>
      <ul className="divide-y divide-[var(--border)] overflow-hidden rounded-[var(--radius-lg)] surface">
        {list.map((tpl) => (
          <li key={tpl.id} className="px-4 py-3 text-sm">
            <p className="font-medium">{tpl.name}</p>
            <p className="mt-1 font-mono text-xs text-[var(--muted)]">
              {tpl.slug} · {tpl.category} · {tpl.steps?.length ?? 0} steps
            </p>
          </li>
        ))}
      </ul>
      {list.length === 0 && !templates.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("workflowsEmpty")}</p>
      ) : null}
    </div>
  );
}

export function AdminModerationPanel() {
  const t = useTranslations("admin");

  const queue = useQuery({
    queryKey: ["admin-moderation-queue"],
    queryFn: () => api.moderation.queue(),
    retry: false,
  });

  const reviews = queue.data?.reviews ?? [];
  const comments = queue.data?.comments ?? [];
  const list = [
    ...reviews.map((r) => ({ ...r, type: "review" as const })),
    ...comments.map((c) => ({ ...c, type: "comment" as const })),
  ];

  return (
    <div className="mt-8 space-y-4">
      <h2 className="font-display text-xl font-semibold">{t("moderationTitle")}</h2>
      <p className="text-sm text-[var(--muted)]">{t("moderationSupporting")}</p>
      <ul className="space-y-3">
        {list.map((item) => (
          <li
            key={`${item.type}-${item.id}`}
            className="surface rounded-[var(--radius-lg)] p-4 text-sm"
          >
            <p className="font-medium">
              {item.type} #{item.id}
            </p>
            <p className="mt-1 text-xs text-[var(--muted)]">
              {item.status ?? "pending"} · {String(item.tool ?? "")}
            </p>
            {item.body ? (
              <p className="mt-2 text-[var(--muted)]">{item.body}</p>
            ) : null}
          </li>
        ))}
      </ul>
      {list.length === 0 && !queue.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("moderationEmpty")}</p>
      ) : null}
    </div>
  );
}

export function AdminCreatorsPanel() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();

  const submissions = useQuery({
    queryKey: ["admin-creator-submissions"],
    queryFn: () => api.creator.adminSubmissions(),
    retry: false,
  });

  const approve = useMutation({
    mutationFn: (id: number) => api.creator.approve(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["admin-creator-submissions"],
      });
    },
  });

  const reject = useMutation({
    mutationFn: (id: number) => api.creator.reject(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["admin-creator-submissions"],
      });
    },
  });

  const rollup = useMutation({
    mutationFn: () => api.creator.adminRollup(),
  });

  const list = asList(submissions.data);

  return (
    <div className="mt-8 space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="font-display text-xl font-semibold">{t("creatorsTitle")}</h2>
          <p className="mt-1 text-sm text-[var(--muted)]">{t("creatorsSupporting")}</p>
        </div>
        <Button
          type="button"
          size="sm"
          variant="secondary"
          disabled={rollup.isPending}
          onClick={() => rollup.mutate()}
        >
          {t("gtmCreatorRollup")}
        </Button>
      </div>
      <ul className="space-y-3">
        {list.map((sub) => (
          <li key={sub.id} className="surface rounded-[var(--radius-lg)] p-4 text-sm">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="font-medium">
                  #{sub.id} · {sub.type} · {sub.status}
                </p>
                <pre className="mt-2 max-h-32 overflow-auto text-xs text-[var(--muted)]">
                  {JSON.stringify(sub.payload, null, 2)}
                </pre>
              </div>
              {sub.status === "pending" ? (
                <div className="flex gap-2">
                  <Button
                    type="button"
                    size="sm"
                    onClick={() => approve.mutate(sub.id)}
                  >
                    {t("creatorsApprove")}
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="secondary"
                    onClick={() => reject.mutate(sub.id)}
                  >
                    {t("creatorsReject")}
                  </Button>
                </div>
              ) : null}
            </div>
          </li>
        ))}
      </ul>
      {list.length === 0 && !submissions.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("creatorsEmpty")}</p>
      ) : null}
    </div>
  );
}

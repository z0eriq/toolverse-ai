"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

function asList<T>(data: T[] | { results: T[] } | undefined): T[] {
  if (!data) return [];
  return Array.isArray(data) ? data : data.results;
}

function asChecks(
  data: { checks?: unknown[] } | unknown[] | undefined,
): { key: string; category: string; status: string; detail: string }[] {
  if (!data) return [];
  if (Array.isArray(data)) return data as never;
  if (Array.isArray(data.checks)) return data.checks as never;
  return [];
}

export function AdminCommandCenterPanel() {
  const t = useTranslations("admin");
  const cc = useQuery({
    queryKey: ["admin-command-center"],
    queryFn: () => api.commandCenter(30),
    retry: false,
  });

  const d = cc.data;
  const cards = d
    ? [
        ["DAU", d.dau],
        ["MAU", d.mau],
        [t("gtmRegistrations"), d.registrations],
        [t("gtmExecutions"), d.tool_executions],
        [t("gtmPremiumConv"), d.premium_conversions],
        [t("gtmRevenue"), `$${(d.revenue_cents / 100).toFixed(2)}`],
        [t("gtmApiUsage"), d.api_usage_units],
        [t("gtmSeoClicks"), d.seo_clicks],
        [t("gtmSeoImpressions"), d.seo_impressions],
        ["AdSense ready", d.adsense_ready ? "Yes" : "No"],
        ["Open campaigns", d.open_campaigns ?? 0],
        ["Indexed URLs", d.indexed_urls_count ?? 0],
        ["Draft tool specs", d.draft_tool_specs_count ?? 0],
      ]
    : [];

  return (
    <div className="mt-8 space-y-8">
      <div>
        <h2 className="font-display text-xl font-semibold">{t("gtmCommandTitle")}</h2>
        <p className="mt-1 text-sm text-[var(--muted)]">{t("gtmCommandSupporting")}</p>
        {d?.deploy_release ? (
          <p className="mt-2 font-mono text-xs text-[var(--muted)]">
            Release: {d.deploy_release}
          </p>
        ) : null}
      </div>
      {cc.isError ? (
        <p className="text-[var(--color-danger)]" role="alert">
          {t("gtmError")}
        </p>
      ) : null}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map(([label, value]) => (
          <Card key={String(label)}>
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
              {label}
            </p>
            <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
              {value}
            </p>
          </Card>
        ))}
      </div>
      {d?.funnel?.steps?.length ? (
        <section>
          <h3 className="font-display text-lg font-semibold">Conversion funnel</h3>
          <p className="mt-1 text-sm text-[var(--muted)]">
            Completion {(d.funnel.completion_rate * 100).toFixed(1)}% · Conversion{" "}
            {(d.funnel.conversion_rate * 100).toFixed(1)}%
          </p>
          <ul className="mt-3 divide-y divide-[var(--border)] surface overflow-hidden rounded-[var(--radius-lg)]">
            {d.funnel.steps.map((step) => (
              <li
                key={step.key}
                className="flex justify-between px-4 py-2 text-sm"
              >
                <span>{step.label}</span>
                <span className="tabular-nums text-[var(--muted)]">{step.count}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      {d?.top_tools?.length ? (
        <section>
          <h3 className="font-display text-lg font-semibold">{t("topTools")}</h3>
          <ul className="mt-3 divide-y divide-[var(--border)] surface overflow-hidden rounded-[var(--radius-lg)]">
            {d.top_tools.map((row) => (
              <li
                key={row.tool_id}
                className="flex justify-between px-4 py-2 text-sm font-mono"
              >
                <span>{row.tool_id}</span>
                <span className="tabular-nums text-[var(--muted)]">{row.count}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      {d?.countries?.length ? (
        <section>
          <h3 className="font-display text-lg font-semibold">{t("gtmCountries")}</h3>
          <ul className="mt-3 divide-y divide-[var(--border)] surface overflow-hidden rounded-[var(--radius-lg)]">
            {d.countries.map((row) => (
              <li
                key={row.country || "unknown"}
                className="flex justify-between px-4 py-2 text-sm"
              >
                <span>{row.country || "—"}</span>
                <span className="tabular-nums text-[var(--muted)]">{row.count}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}

export function AdminToolScoresPanel() {
  const t = useTranslations("admin");
  const scores = useQuery({
    queryKey: ["admin-tool-scores"],
    queryFn: () => api.toolScores(),
    retry: false,
  });
  const list = asList(scores.data);

  return (
    <div className="mt-8 space-y-4">
      <h2 className="font-display text-xl font-semibold">{t("gtmToolScoresTitle")}</h2>
      <p className="text-sm text-[var(--muted)]">{t("gtmToolScoresSupporting")}</p>
      <div className="overflow-x-auto rounded-[var(--radius-lg)] surface">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="border-b border-[var(--border)] text-xs uppercase text-[var(--muted)]">
            <tr>
              <th className="px-4 py-3">Tool</th>
              <th className="px-4 py-3">Traffic</th>
              <th className="px-4 py-3">Usage</th>
              <th className="px-4 py-3">Revenue</th>
              <th className="px-4 py-3">SEO</th>
              <th className="px-4 py-3">Retention</th>
              <th className="px-4 py-3">Priority</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border)]">
            {list.map((row) => (
              <tr key={row.id}>
                <td className="px-4 py-3 font-mono text-xs">
                  {row.tool_slug ?? row.tool}
                </td>
                <td className="px-4 py-3 tabular-nums">
                  {Number(row.traffic_score).toFixed(0)}
                </td>
                <td className="px-4 py-3 tabular-nums">
                  {Number(row.usage_score).toFixed(0)}
                </td>
                <td className="px-4 py-3 tabular-nums">
                  {Number(row.revenue_score).toFixed(0)}
                </td>
                <td className="px-4 py-3 tabular-nums">
                  {Number(row.seo_score).toFixed(0)}
                </td>
                <td className="px-4 py-3 tabular-nums">
                  {Number(row.retention_score).toFixed(0)}
                </td>
                <td className="px-4 py-3 font-semibold tabular-nums">
                  {Number(row.priority_score).toFixed(0)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {list.length === 0 && !scores.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("gtmToolScoresEmpty")}</p>
      ) : null}
    </div>
  );
}

export function AdminSeoOpportunityTasksSection() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();
  const tasks = useQuery({
    queryKey: ["admin-seo-opp-tasks"],
    queryFn: () => api.seoOpportunityTasks.list(),
    retry: false,
  });
  const generate = useMutation({
    mutationFn: () => api.seoOpportunityTasks.generate(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-seo-opp-tasks"] });
    },
  });
  const update = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      api.seoOpportunityTasks.update(id, status),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-seo-opp-tasks"] });
    },
  });
  const list = asList(tasks.data);

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="font-display text-lg font-semibold">
            {t("gtmSeoTasksTitle")}
          </h3>
          <p className="mt-1 text-sm text-[var(--muted)]">
            {t("gtmSeoTasksSupporting")}
          </p>
        </div>
        <Button
          type="button"
          size="sm"
          disabled={generate.isPending}
          onClick={() => generate.mutate()}
        >
          {t("gtmSeoTasksGenerate")}
        </Button>
      </div>
      <ul className="space-y-3">
        {list.map((task) => (
          <li key={task.id} className="surface rounded-[var(--radius-lg)] p-4 text-sm">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="font-medium">{task.title}</p>
                <p className="mt-1 text-xs text-[var(--muted)]">
                  {task.source} · {task.suggested_action} · {task.status} · p
                  {task.priority}
                </p>
                <p className="mt-2 text-[var(--muted)]">{task.rationale}</p>
              </div>
              {task.status === "open" ? (
                <Button
                  type="button"
                  size="sm"
                  variant="secondary"
                  onClick={() => update.mutate({ id: task.id, status: "done" })}
                >
                  {t("gtmMarkDone")}
                </Button>
              ) : null}
            </div>
          </li>
        ))}
      </ul>
      {list.length === 0 && !tasks.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("gtmSeoTasksEmpty")}</p>
      ) : null}
    </section>
  );
}

export function AdminGrowthTasksSection() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();
  const tasks = useQuery({
    queryKey: ["admin-growth-tasks"],
    queryFn: () => api.growthTasks.list(),
    retry: false,
  });
  const accept = useMutation({
    mutationFn: (id: number) => api.growthTasks.accept(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-growth-tasks"] });
    },
  });
  const complete = useMutation({
    mutationFn: (id: number) => api.growthTasks.complete(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-growth-tasks"] });
    },
  });
  const list = asList(tasks.data);

  return (
    <section className="mt-8 space-y-4">
      <h3 className="font-display text-lg font-semibold">{t("gtmGrowthTasksTitle")}</h3>
      <ul className="space-y-3">
        {list.map((task) => (
          <li key={task.id} className="surface rounded-[var(--radius-lg)] p-4 text-sm">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="font-medium">
                  [{task.category}] {task.title}
                </p>
                <p className="mt-1 text-xs text-[var(--muted)]">
                  {task.status} · priority {task.priority}
                </p>
              </div>
              <div className="flex gap-2">
                {task.status === "open" ? (
                  <Button type="button" size="sm" onClick={() => accept.mutate(task.id)}>
                    {t("growthAgentAccept")}
                  </Button>
                ) : null}
                {task.status === "accepted" || task.status === "open" ? (
                  <Button
                    type="button"
                    size="sm"
                    variant="secondary"
                    onClick={() => complete.mutate(task.id)}
                  >
                    {t("gtmMarkDone")}
                  </Button>
                ) : null}
              </div>
            </div>
          </li>
        ))}
      </ul>
      {list.length === 0 && !tasks.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("gtmGrowthTasksEmpty")}</p>
      ) : null}
    </section>
  );
}

export function AdminLaunchReadinessPanel() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();
  const readiness = useQuery({
    queryKey: ["admin-launch-readiness"],
    queryFn: () => api.launchReadiness.get(),
    retry: false,
  });
  const run = useMutation({
    mutationFn: () => api.launchReadiness.run(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-launch-readiness"] });
    },
  });
  const checks = asChecks(readiness.data);

  return (
    <div className="mt-8 space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="font-display text-xl font-semibold">
            {t("gtmReadinessTitle")}
          </h2>
          <p className="mt-1 text-sm text-[var(--muted)]">
            {t("gtmReadinessSupporting")}
          </p>
        </div>
        <Button type="button" disabled={run.isPending} onClick={() => run.mutate()}>
          {t("gtmReadinessRun")}
        </Button>
      </div>
      <ul className="space-y-2">
        {checks.map((c) => (
          <li
            key={c.key}
            className="flex flex-wrap items-start justify-between gap-2 surface rounded-[var(--radius-md)] px-4 py-3 text-sm"
          >
            <div>
              <p className="font-medium">
                {c.category}: {c.key}
              </p>
              <p className="mt-1 text-xs text-[var(--muted)]">{c.detail}</p>
            </div>
            <span
              className={
                c.status === "pass"
                  ? "text-[var(--accent)]"
                  : c.status === "fail"
                    ? "text-[var(--color-danger)]"
                    : "text-[var(--muted)]"
              }
            >
              {c.status}
            </span>
          </li>
        ))}
      </ul>
      {checks.length === 0 && !readiness.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("gtmReadinessEmpty")}</p>
      ) : null}
    </div>
  );
}

export function AdminSalesLeadsPanel() {
  const t = useTranslations("admin");
  const leads = useQuery({
    queryKey: ["admin-sales-leads"],
    queryFn: () => api.salesLeads.adminList(),
    retry: false,
  });
  const list = asList(leads.data);

  return (
    <div className="mt-8 space-y-4">
      <h2 className="font-display text-xl font-semibold">{t("gtmLeadsTitle")}</h2>
      <ul className="space-y-3">
        {list.map((lead) => (
          <li key={lead.id} className="surface rounded-[var(--radius-lg)] p-4 text-sm">
            <p className="font-medium">
              {lead.name} · {lead.email}
            </p>
            <p className="mt-1 text-xs text-[var(--muted)]">
              {lead.intent} · {lead.status} · {lead.company}
            </p>
            {lead.message ? (
              <p className="mt-2 text-[var(--muted)]">{lead.message}</p>
            ) : null}
          </li>
        ))}
      </ul>
      {list.length === 0 && !leads.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("gtmLeadsEmpty")}</p>
      ) : null}
    </div>
  );
}

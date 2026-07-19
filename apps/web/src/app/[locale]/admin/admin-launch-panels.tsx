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

export function AdminIntelligencePanel() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();

  const opportunities = useQuery({
    queryKey: ["admin-opportunities"],
    queryFn: () => api.opportunities.list(),
    retry: false,
  });

  const queueMutation = useMutation({
    mutationFn: (id: number) => api.opportunities.queue(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-opportunities"] });
    },
  });

  const list = asList(opportunities.data);

  return (
    <div className="mt-8 space-y-4">
      <h2 className="font-display text-xl font-semibold">{t("intelTitle")}</h2>
      <p className="text-sm text-[var(--muted)]">{t("intelSupporting")}</p>
      {opportunities.isError ? (
        <p className="text-[var(--color-danger)]" role="alert">
          {t("intelError")}
        </p>
      ) : null}
      <ul className="divide-y divide-[var(--border)] overflow-hidden rounded-[var(--radius-lg)] surface">
        {list.map((row) => (
          <li
            key={row.id}
            className="flex flex-wrap items-start justify-between gap-3 px-4 py-3 text-sm"
          >
            <div className="min-w-0 flex-1">
              <p className="font-medium">{row.title || row.suggested_slug}</p>
              <p className="mt-1 font-mono text-xs text-[var(--muted)]">
                {row.suggested_slug} · {row.category_slug} · {row.status} · score{" "}
                {Number(row.priority_score).toFixed(2)}
              </p>
              {row.rationale ? (
                <p className="mt-1 text-xs text-[var(--muted)]">{row.rationale}</p>
              ) : null}
            </div>
            <Button
              type="button"
              size="sm"
              disabled={
                queueMutation.isPending ||
                row.status === "queued" ||
                row.status === "built"
              }
              onClick={() => queueMutation.mutate(row.id)}
            >
              {t("intelQueue")}
            </Button>
          </li>
        ))}
      </ul>
      {list.length === 0 && !opportunities.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("intelEmpty")}</p>
      ) : null}
    </div>
  );
}

export function AdminKeywordsPanel() {
  const t = useTranslations("admin");

  const keywords = useQuery({
    queryKey: ["admin-keywords-top"],
    queryFn: () => api.keywords.top(50),
    retry: false,
  });

  const list = asList(keywords.data);

  return (
    <div className="mt-8 space-y-4">
      <h2 className="font-display text-xl font-semibold">{t("keywordsTitle")}</h2>
      <p className="text-sm text-[var(--muted)]">{t("keywordsSupporting")}</p>
      {keywords.isError ? (
        <p className="text-[var(--color-danger)]" role="alert">
          {t("keywordsError")}
        </p>
      ) : null}
      <div className="overflow-x-auto rounded-[var(--radius-lg)] surface">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="border-b border-[var(--border)] text-xs uppercase tracking-wider text-[var(--muted)]">
            <tr>
              <th className="px-4 py-3 font-medium">{t("keywordsColKeyword")}</th>
              <th className="px-4 py-3 font-medium">{t("keywordsColVolume")}</th>
              <th className="px-4 py-3 font-medium">{t("keywordsColDiff")}</th>
              <th className="px-4 py-3 font-medium">{t("keywordsColPos")}</th>
              <th className="px-4 py-3 font-medium">{t("keywordsColScore")}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border)]">
            {list.map((row) => (
              <tr key={row.id}>
                <td className="px-4 py-3">
                  <span className="font-medium">{row.keyword}</span>
                  {row.suggested_tool_slug ? (
                    <span className="mt-0.5 block font-mono text-xs text-[var(--muted)]">
                      → {row.suggested_tool_slug}
                    </span>
                  ) : null}
                </td>
                <td className="px-4 py-3 tabular-nums">{row.search_volume}</td>
                <td className="px-4 py-3 tabular-nums">{row.difficulty}</td>
                <td className="px-4 py-3 tabular-nums">
                  {row.ranking_position != null
                    ? Number(row.ranking_position).toFixed(1)
                    : "—"}
                </td>
                <td className="px-4 py-3 tabular-nums">
                  {Number(row.priority_score).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {list.length === 0 && !keywords.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("keywordsEmpty")}</p>
      ) : null}
    </div>
  );
}

export function AdminAutopilotPanel() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();
  const [keywordId, setKeywordId] = useState("");

  const runs = useQuery({
    queryKey: ["admin-autopilot-runs"],
    queryFn: () => api.autopilot.listRuns(),
    retry: false,
  });

  const startMutation = useMutation({
    mutationFn: () =>
      api.autopilot.startRun(Number(keywordId), { async_mode: true }),
    onSuccess: async () => {
      setKeywordId("");
      await queryClient.invalidateQueries({ queryKey: ["admin-autopilot-runs"] });
    },
  });

  const approveMutation = useMutation({
    mutationFn: (id: number) => api.autopilot.approve(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-autopilot-runs"] });
    },
  });

  const list = asList(runs.data);

  return (
    <div className="mt-8 space-y-6">
      <div>
        <h2 className="font-display text-xl font-semibold">{t("autopilotTitle")}</h2>
        <p className="mt-1 text-sm text-[var(--muted)]">{t("autopilotSupporting")}</p>
      </div>
      <Card>
        <form
          className="flex flex-wrap items-end gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            startMutation.mutate();
          }}
        >
          <div className="min-w-[200px] flex-1">
            <Label htmlFor="autopilot-kw">{t("autopilotKeywordId")}</Label>
            <Input
              id="autopilot-kw"
              type="number"
              min={1}
              required
              value={keywordId}
              onChange={(e) => setKeywordId(e.target.value)}
            />
          </div>
          <Button type="submit" disabled={startMutation.isPending}>
            {startMutation.isPending ? t("autopilotStarting") : t("autopilotStart")}
          </Button>
        </form>
        {startMutation.isError ? (
          <p className="mt-3 text-sm text-[var(--color-danger)]" role="alert">
            {startMutation.error instanceof ApiError
              ? startMutation.error.message
              : t("autopilotError")}
          </p>
        ) : null}
      </Card>
      <ul className="space-y-3">
        {list.map((run) => (
          <li key={run.id} className="surface rounded-[var(--radius-lg)] p-4 text-sm">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="font-medium">
                  #{run.id} · {run.status} · {run.stage}
                </p>
                <p className="mt-1 text-xs text-[var(--muted)]">
                  keyword={run.keyword ?? "—"} · quality=
                  {run.quality_score != null
                    ? Number(run.quality_score).toFixed(2)
                    : "—"}
                  {run.is_duplicate ? " · duplicate" : ""}
                </p>
                {run.error ? (
                  <p className="mt-1 text-xs text-[var(--color-danger)]">{run.error}</p>
                ) : null}
              </div>
              {run.status === "human_review" ? (
                <Button
                  type="button"
                  size="sm"
                  disabled={approveMutation.isPending}
                  onClick={() => approveMutation.mutate(run.id)}
                >
                  {t("autopilotApprove")}
                </Button>
              ) : null}
            </div>
          </li>
        ))}
      </ul>
      {list.length === 0 && !runs.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("autopilotEmpty")}</p>
      ) : null}
    </div>
  );
}

export function AdminEmailPanel() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();
  const [slug, setSlug] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [testEmail, setTestEmail] = useState("");

  const campaigns = useQuery({
    queryKey: ["admin-email-campaigns"],
    queryFn: () => api.email.campaigns(),
    retry: false,
  });

  const createMutation = useMutation({
    mutationFn: () =>
      api.email.createCampaign({
        slug: slug.trim(),
        subject: subject.trim(),
        body_html: body.trim(),
      }),
    onSuccess: async () => {
      setSlug("");
      setSubject("");
      setBody("");
      await queryClient.invalidateQueries({ queryKey: ["admin-email-campaigns"] });
    },
  });

  const sendTestMutation = useMutation({
    mutationFn: (id: number) => api.email.sendTest(id, testEmail.trim()),
  });

  const list = asList(campaigns.data);

  return (
    <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_1fr]">
      <Card>
        <h2 className="font-display text-xl font-semibold">{t("emailTitle")}</h2>
        <p className="mt-1 text-sm text-[var(--muted)]">{t("emailSupporting")}</p>
        <form
          className="mt-6 space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            createMutation.mutate();
          }}
        >
          <div>
            <Label htmlFor="email-slug">{t("emailSlug")}</Label>
            <Input
              id="email-slug"
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
              required
              pattern="[a-z0-9-]+"
            />
          </div>
          <div>
            <Label htmlFor="email-subject">{t("emailSubject")}</Label>
            <Input
              id="email-subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              required
            />
          </div>
          <div>
            <Label htmlFor="email-body">{t("emailBody")}</Label>
            <textarea
              id="email-body"
              className="mt-1 min-h-[120px] w-full rounded-[var(--radius-md)] border border-[var(--border)] bg-transparent px-3 py-2 text-sm"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              required
            />
          </div>
          <Button type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending ? t("emailSaving") : t("emailCreate")}
          </Button>
        </form>
      </Card>
      <div>
        <div className="mb-4">
          <Label htmlFor="email-test">{t("emailTestTo")}</Label>
          <Input
            id="email-test"
            type="email"
            value={testEmail}
            onChange={(e) => setTestEmail(e.target.value)}
            placeholder="you@example.com"
          />
        </div>
        <ul className="space-y-3">
          {list.map((c) => (
            <li key={c.id} className="surface rounded-[var(--radius-lg)] p-4 text-sm">
              <p className="font-medium">{c.slug}</p>
              <p className="mt-1 text-xs text-[var(--muted)]">
                {c.subject} · {c.status}
              </p>
              <Button
                type="button"
                size="sm"
                className="mt-3"
                disabled={sendTestMutation.isPending || !testEmail.trim()}
                onClick={() => sendTestMutation.mutate(c.id)}
              >
                {t("emailSendTest")}
              </Button>
            </li>
          ))}
        </ul>
        {list.length === 0 && !campaigns.isLoading ? (
          <p className="text-sm text-[var(--muted)]">{t("emailEmpty")}</p>
        ) : null}
      </div>
    </div>
  );
}

export function AdminExperimentsPanel() {
  const t = useTranslations("admin");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const experiments = useQuery({
    queryKey: ["admin-experiments"],
    queryFn: () => api.experiments.adminList(),
    retry: false,
  });

  const results = useQuery({
    queryKey: ["admin-experiment-results", selectedId],
    queryFn: () => api.experiments.adminResults(selectedId!),
    enabled: selectedId != null,
    retry: false,
  });

  const list = asList(experiments.data);

  return (
    <div className="mt-8 space-y-6">
      <h2 className="font-display text-xl font-semibold">{t("expTitle")}</h2>
      <p className="text-sm text-[var(--muted)]">{t("expSupporting")}</p>
      <ul className="space-y-2">
        {list.map((exp) => (
          <li key={exp.id}>
            <button
              type="button"
              className="w-full rounded-[var(--radius-lg)] surface px-4 py-3 text-left text-sm transition hover:bg-[color-mix(in_oklab,var(--foreground)_4%,transparent)]"
              onClick={() => setSelectedId(exp.id)}
            >
              <span className="font-medium">{exp.name || exp.key}</span>
              <span className="ms-2 text-xs text-[var(--muted)]">
                {exp.key} · {exp.is_active ? "active" : "inactive"}
              </span>
            </button>
          </li>
        ))}
      </ul>
      {list.length === 0 && !experiments.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("expEmpty")}</p>
      ) : null}
      {results.data ? (
        <Card>
          <h3 className="font-display text-lg font-semibold">{t("expResults")}</h3>
          <pre className="mt-3 overflow-x-auto text-xs text-[var(--muted)]">
            {JSON.stringify(results.data, null, 2)}
          </pre>
        </Card>
      ) : null}
    </div>
  );
}

export function AdminLimitsPanel() {
  const t = useTranslations("admin");

  const plans = useQuery({
    queryKey: ["admin-plans-limits"],
    queryFn: () => api.plans(),
    retry: false,
  });

  const invoices = useQuery({
    queryKey: ["admin-marketplace-invoices"],
    queryFn: () => api.marketplace.adminInvoices(),
    retry: false,
  });

  return (
    <div className="mt-8 space-y-8">
      <div>
        <h2 className="font-display text-xl font-semibold">{t("limitsTitle")}</h2>
        <p className="mt-1 text-sm text-[var(--muted)]">{t("limitsSupporting")}</p>
        <p className="mt-2 text-sm">
          <Link href="/pricing" className="text-[var(--accent)] hover:underline">
            {t("limitsPricingLink")}
          </Link>
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        {(plans.data ?? []).map((plan) => (
          <Card key={plan.slug}>
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
              {plan.slug === "premium" ? "Pro" : plan.name}
            </p>
            <p className="mt-1 font-mono text-xs text-[var(--muted)]">{plan.slug}</p>
            <ul className="mt-4 space-y-1 text-sm text-[var(--muted)]">
              <li>
                {t("limitsToolRuns")}:{" "}
                {plan.monthly_tool_runs === -1
                  ? t("limitsUnlimited")
                  : (plan.monthly_tool_runs ?? "—")}
              </li>
              <li>
                {t("limitsApiQuota")}: {plan.api_monthly_quota ?? "—"}
              </li>
              <li>
                {t("limitsAdsFree")}:{" "}
                {plan.ads_free ? t("limitsYes") : t("limitsNo")}
              </li>
              <li>
                {t("limitsHistoryDays")}: {plan.history_days ?? "—"}
              </li>
            </ul>
          </Card>
        ))}
      </div>
      <section>
        <h3 className="font-display text-lg font-semibold">{t("enterpriseInvoices")}</h3>
        <ul className="mt-3 space-y-2 text-sm">
          {asList(invoices.data).map((inv) => (
            <li key={inv.id} className="surface rounded-[var(--radius-md)] px-3 py-2">
              #{inv.id} · org={inv.org} · {inv.status} · {inv.usage_units} units · $
              {(inv.amount_cents / 100).toFixed(2)}
            </li>
          ))}
        </ul>
        {asList(invoices.data).length === 0 && !invoices.isLoading ? (
          <p className="mt-2 text-sm text-[var(--muted)]">{t("enterpriseInvoicesEmpty")}</p>
        ) : null}
      </section>
    </div>
  );
}

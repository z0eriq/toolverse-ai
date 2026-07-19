"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import {
  ApiError,
  api,
  type DynamicToolDefinition,
  type DynamicUiSchema,
} from "@/lib/api";
import { useAuth } from "@/features/auth/auth-context";
import { Card } from "@/components/ui/card";
import { Link } from "@/i18n/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { cn, localize } from "@/lib/utils";
import {
  AdminContentPanel,
  AdminFactoryPanel,
  AdminRevenuePanel,
  AdminSeoPanel,
  AdminToolsGrowthPanel,
} from "./admin-engine-panels";
import {
  AdminAutopilotPanel,
  AdminEmailPanel,
  AdminExperimentsPanel,
  AdminIntelligencePanel,
  AdminKeywordsPanel,
  AdminLimitsPanel,
} from "./admin-launch-panels";
import {
  AdminCreatorsPanel,
  AdminGrowthAgentPanel,
  AdminModerationPanel,
  AdminWorkflowsPanel,
} from "./admin-scale-panels";
import {
  AdminCommandCenterPanel,
  AdminGrowthTasksSection,
  AdminLaunchReadinessPanel,
  AdminSalesLeadsPanel,
  AdminToolScoresPanel,
} from "./admin-gtm-panels";
import {
  AdminBacklinksPanel,
  AdminCompetitorsPanel,
} from "./admin-domination-panels";

type AdminTab =
  | "overview"
  | "commandCenter"
  | "builder"
  | "analytics"
  | "growth"
  | "apiKeys"
  | "aiUsage"
  | "factory"
  | "seo"
  | "revenue"
  | "toolsGrowth"
  | "content"
  | "intelligence"
  | "keywords"
  | "toolScores"
  | "autopilot"
  | "email"
  | "experiments"
  | "limits"
  | "growthAgent"
  | "workflows"
  | "moderation"
  | "creators"
  | "launchReadiness"
  | "salesLeads"
  | "competitors"
  | "backlinks";

const DEFAULT_UI_SCHEMA = `{
  "fields": [
    {
      "name": "input",
      "type": "textarea",
      "label": "Input",
      "required": true
    }
  ]
}`;

const DEFAULT_PIPELINE = `[
  {
    "type": "transform",
    "op": "trim",
    "source": "input.input",
    "target": "output"
  }
]`;

function CssBar({
  label,
  value,
  max,
}: {
  label: string;
  value: number;
  max: number;
}) {
  const pct = max > 0 ? Math.max(2, Math.round((value / max) * 100)) : 0;
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between gap-2 text-sm">
        <span className="truncate font-mono text-xs">{label}</span>
        <span className="tabular-nums text-[var(--muted)]">{value}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-[color-mix(in_oklab,var(--foreground)_8%,transparent)]">
        <div
          className="h-full rounded-full bg-[var(--accent)]"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function AdminPage() {
  const t = useTranslations("admin");
  const { user, isLoading } = useAuth();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<AdminTab>("overview");
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);
  const [slug, setSlug] = useState("");
  const [nameEn, setNameEn] = useState("");
  const [category, setCategory] = useState("ai");
  const [uiSchemaText, setUiSchemaText] = useState(DEFAULT_UI_SCHEMA);
  const [pipelineText, setPipelineText] = useState(DEFAULT_PIPELINE);

  const isAdmin =
    user &&
    (user.role === "admin" ||
      user.role === "staff" ||
      String(user.role).toLowerCase() === "admin");

  const metrics = useQuery({
    queryKey: ["admin-metrics"],
    queryFn: () => api.adminMetrics(),
    enabled: Boolean(isAdmin),
    retry: false,
  });

  const dynamicTools = useQuery({
    queryKey: ["admin-dynamic-tools"],
    queryFn: () => api.listDynamicTools(),
    enabled: Boolean(isAdmin) && (tab === "builder" || tab === "overview"),
    retry: false,
  });

  const analytics = useQuery({
    queryKey: ["admin-analytics-dashboard"],
    queryFn: () => api.analyticsDashboard(),
    enabled: Boolean(isAdmin) && tab === "analytics",
    retry: false,
  });

  const growth = useQuery({
    queryKey: ["admin-growth-dashboard"],
    queryFn: () => api.growthDashboard(),
    enabled: Boolean(isAdmin) && tab === "growth",
    retry: false,
  });

  const aiUsage = useQuery({
    queryKey: ["admin-ai-usage"],
    queryFn: () => api.aiUsage(),
    enabled: Boolean(isAdmin) && (tab === "aiUsage" || tab === "apiKeys"),
    retry: false,
  });

  const createMutation = useMutation({
    mutationFn: () => {
      const ui_schema = JSON.parse(uiSchemaText) as DynamicUiSchema;
      const pipeline = JSON.parse(pipelineText) as unknown[];
      return api.createDynamicTool({
        slug: slug.trim(),
        category_slug: category.trim(),
        name: { en: nameEn.trim() },
        description: { en: nameEn.trim() },
        ui_schema,
        pipeline,
        capabilities: ["server"],
      });
    },
    onSuccess: async () => {
      setFormError(null);
      setFormSuccess(t("builderCreated"));
      setSlug("");
      setNameEn("");
      await queryClient.invalidateQueries({ queryKey: ["admin-dynamic-tools"] });
    },
    onError: (err) => {
      setFormSuccess(null);
      setFormError(
        err instanceof ApiError
          ? err.message
          : err instanceof SyntaxError
            ? t("builderJsonError")
            : t("builderError"),
      );
    },
  });

  const publishMutation = useMutation({
    mutationFn: (id: number) => api.publishDynamicTool(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-dynamic-tools"] });
    },
  });

  const tabs = useMemo(
    () =>
      [
        { id: "overview" as const, label: t("tabOverview") },
        { id: "commandCenter" as const, label: t("tabCommandCenter") },
        { id: "builder" as const, label: t("tabBuilder") },
        { id: "factory" as const, label: t("tabFactory") },
        { id: "analytics" as const, label: t("tabAnalytics") },
        { id: "growth" as const, label: t("tabGrowth") },
        { id: "seo" as const, label: t("tabSeo") },
        { id: "revenue" as const, label: t("tabRevenue") },
        { id: "toolsGrowth" as const, label: t("tabToolsGrowth") },
        { id: "content" as const, label: t("tabContent") },
        { id: "intelligence" as const, label: t("tabIntelligence") },
        { id: "toolScores" as const, label: t("tabToolScores") },
        { id: "keywords" as const, label: t("tabKeywords") },
        { id: "autopilot" as const, label: t("tabAutopilot") },
        { id: "email" as const, label: t("tabEmail") },
        { id: "experiments" as const, label: t("tabExperiments") },
        { id: "limits" as const, label: t("tabLimits") },
        { id: "growthAgent" as const, label: t("tabGrowthAgent") },
        { id: "competitors" as const, label: t("tabCompetitors") },
        { id: "backlinks" as const, label: t("tabBacklinks") },
        { id: "workflows" as const, label: t("tabWorkflows") },
        { id: "moderation" as const, label: t("tabModeration") },
        { id: "creators" as const, label: t("tabCreators") },
        { id: "salesLeads" as const, label: t("tabSalesLeads") },
        { id: "launchReadiness" as const, label: t("tabLaunchReadiness") },
        { id: "apiKeys" as const, label: t("tabApiKeys") },
        { id: "aiUsage" as const, label: t("tabAiUsage") },
      ] satisfies { id: AdminTab; label: string }[],
    [t],
  );

  if (isLoading) return <div className="p-8">…</div>;

  if (!user || !isAdmin) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h1 className="font-display text-3xl font-semibold">{t("title")}</h1>
        <p className="mt-2 text-[var(--muted)]">{t("unauthorized")}</p>
        <Button asChild className="mt-6">
          <Link href="/">Home</Link>
        </Button>
      </div>
    );
  }

  const data = metrics.data;
  const cards = data
    ? [
        [t("users"), data.users],
        [t("tools"), data.tools],
        [t("premiumTools"), data.premium_tools],
        [t("history"), data.history_events],
        [t("analytics"), data.analytics_events],
        [t("posts"), data.blog_posts],
        [t("subscribers"), data.premium_subscribers],
      ]
    : [];

  const seriesMax = Math.max(
    1,
    ...(analytics.data?.usage_series.map((s) => s.count) ?? [1]),
  );
  const topToolsMax = Math.max(
    1,
    ...(analytics.data?.top_tools.map((s) => s.count) ?? [1]),
  );
  const geoMax = Math.max(1, ...(analytics.data?.geo.map((s) => s.count) ?? [1]));
  const providerMax = Math.max(
    1,
    ...(aiUsage.data?.by_provider.map((s) => s.calls) ?? [1]),
  );
  const growthLangMax = Math.max(
    1,
    ...(growth.data?.languages.map((s) => s.count) ?? [1]),
  );
  const growthSourceMax = Math.max(
    1,
    ...(growth.data?.traffic_sources.map((s) => s.count) ?? [1]),
  );

  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-3xl font-semibold tracking-tight">{t("title")}</h1>
      <p className="mt-2 text-[var(--muted)]">{t("supporting")}</p>

      <div
        className="mt-8 flex flex-wrap gap-2 border-b border-[var(--border)] pb-3"
        role="tablist"
        aria-label={t("tabsLabel")}
      >
        {tabs.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={tab === item.id}
            className={cn(
              "rounded-[var(--radius-md)] px-3 py-2 text-sm transition",
              tab === item.id
                ? "bg-[color-mix(in_oklab,var(--accent)_16%,transparent)] text-[var(--accent)]"
                : "text-[var(--muted)] hover:text-[var(--foreground)]",
            )}
            onClick={() => setTab(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>

      {tab === "overview" ? (
        <div className="mt-8">
          {metrics.isError ? (
            <p className="text-[var(--color-danger)]" role="alert">
              {t("unauthorized")}
            </p>
          ) : null}

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
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

          {data?.top_tools?.length ? (
            <section className="mt-12">
              <h2 className="font-display text-xl font-semibold">{t("topTools")}</h2>
              <ul className="mt-4 divide-y divide-[var(--border)] surface overflow-hidden rounded-[var(--radius-lg)]">
                {data.top_tools.map((tool) => (
                  <li
                    key={tool.tool_id}
                    className="flex items-center justify-between px-4 py-3 text-sm"
                  >
                    <span className="font-mono">{tool.slug}</span>
                    <span className="tabular-nums text-[var(--muted)]">
                      {tool.usage_count}
                    </span>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </div>
      ) : null}

      {tab === "builder" ? (
        <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_1fr]">
          <Card>
            <h2 className="font-display text-xl font-semibold">{t("builderTitle")}</h2>
            <p className="mt-1 text-sm text-[var(--muted)]">{t("builderSupporting")}</p>
            <form
              className="mt-6 space-y-4"
              onSubmit={(e) => {
                e.preventDefault();
                setFormError(null);
                setFormSuccess(null);
                createMutation.mutate();
              }}
            >
              <div>
                <Label htmlFor="dyn-slug">{t("builderSlug")}</Label>
                <Input
                  id="dyn-slug"
                  value={slug}
                  onChange={(e) => setSlug(e.target.value)}
                  placeholder="my-tool"
                  required
                />
              </div>
              <div>
                <Label htmlFor="dyn-name">{t("builderName")}</Label>
                <Input
                  id="dyn-name"
                  value={nameEn}
                  onChange={(e) => setNameEn(e.target.value)}
                  placeholder="My Tool"
                  required
                />
              </div>
              <div>
                <Label htmlFor="dyn-category">{t("builderCategory")}</Label>
                <Input
                  id="dyn-category"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  placeholder="ai"
                  required
                />
              </div>
              <div>
                <Label htmlFor="dyn-ui">{t("builderUiSchema")}</Label>
                <Textarea
                  id="dyn-ui"
                  value={uiSchemaText}
                  onChange={(e) => setUiSchemaText(e.target.value)}
                  rows={10}
                  required
                />
              </div>
              <div>
                <Label htmlFor="dyn-pipeline">{t("builderPipeline")}</Label>
                <Textarea
                  id="dyn-pipeline"
                  value={pipelineText}
                  onChange={(e) => setPipelineText(e.target.value)}
                  rows={10}
                  required
                />
              </div>
              {formError ? (
                <p className="text-sm text-[var(--color-danger)]" role="alert">
                  {formError}
                </p>
              ) : null}
              {formSuccess ? (
                <p className="text-sm text-[var(--accent)]">{formSuccess}</p>
              ) : null}
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? t("builderSaving") : t("builderCreate")}
              </Button>
            </form>
          </Card>

          <div>
            <h2 className="font-display text-xl font-semibold">{t("builderList")}</h2>
            {dynamicTools.isLoading ? (
              <p className="mt-4 text-sm text-[var(--muted)]">{t("loading")}</p>
            ) : null}
            {dynamicTools.isError ? (
              <p className="mt-4 text-sm text-[var(--color-danger)]">{t("builderError")}</p>
            ) : null}
            <ul className="mt-4 space-y-3">
              {(dynamicTools.data ?? []).map((tool: DynamicToolDefinition) => {
                const title =
                  typeof tool.name === "string"
                    ? tool.name
                    : localize(tool.name, "en");
                return (
                  <li key={tool.id} className="surface rounded-[var(--radius-lg)] p-4">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <p className="font-medium">{title}</p>
                        <p className="mt-1 font-mono text-xs text-[var(--muted)]">
                          {tool.slug} · {tool.status} · rev {tool.revision}
                        </p>
                      </div>
                      {tool.status !== "published" ? (
                        <Button
                          type="button"
                          size="sm"
                          variant="secondary"
                          disabled={publishMutation.isPending}
                          onClick={() => publishMutation.mutate(tool.id)}
                        >
                          {t("builderPublish")}
                        </Button>
                      ) : (
                        <Button asChild size="sm" variant="ghost">
                          <Link href={`/tools/${tool.category_slug}/${tool.slug}`}>
                            {t("builderOpen")}
                          </Link>
                        </Button>
                      )}
                    </div>
                  </li>
                );
              })}
            </ul>
            {dynamicTools.data?.length === 0 ? (
              <p className="mt-4 text-sm text-[var(--muted)]">{t("builderEmpty")}</p>
            ) : null}
          </div>
        </div>
      ) : null}

      {tab === "analytics" ? (
        <div className="mt-8 space-y-8">
          {analytics.isError ? (
            <p className="text-[var(--color-danger)]" role="alert">
              {t("analyticsError")}
            </p>
          ) : null}
          {analytics.data ? (
            <>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
                    {t("impressions")}
                  </p>
                  <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
                    {analytics.data.ctr.impressions}
                  </p>
                </Card>
                <Card>
                  <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
                    {t("clicks")}
                  </p>
                  <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
                    {analytics.data.ctr.clicks}
                  </p>
                </Card>
                <Card>
                  <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
                    {t("uses")}
                  </p>
                  <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
                    {analytics.data.ctr.uses}
                  </p>
                </Card>
                <Card>
                  <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
                    CTR
                  </p>
                  <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
                    {(analytics.data.ctr.click_through_rate * 100).toFixed(1)}%
                  </p>
                </Card>
              </div>

              <Card>
                <h2 className="font-display text-lg font-semibold">{t("usageSeries")}</h2>
                <div className="mt-4 space-y-3">
                  {analytics.data.usage_series.slice(-14).map((row) => (
                    <CssBar
                      key={row.date}
                      label={row.date}
                      value={row.count}
                      max={seriesMax}
                    />
                  ))}
                </div>
              </Card>

              <div className="grid gap-6 lg:grid-cols-2">
                <Card>
                  <h2 className="font-display text-lg font-semibold">{t("topTools")}</h2>
                  <div className="mt-4 space-y-3">
                    {analytics.data.top_tools.map((row) => (
                      <CssBar
                        key={row.tool_id}
                        label={row.tool_id}
                        value={row.count}
                        max={topToolsMax}
                      />
                    ))}
                  </div>
                </Card>
                <Card>
                  <h2 className="font-display text-lg font-semibold">{t("geo")}</h2>
                  <div className="mt-4 space-y-3">
                    {analytics.data.geo.map((row) => (
                      <CssBar
                        key={row.country}
                        label={row.country}
                        value={row.count}
                        max={geoMax}
                      />
                    ))}
                  </div>
                </Card>
              </div>

              <Card>
                <h2 className="font-display text-lg font-semibold">{t("retention")}</h2>
                <dl className="mt-4 grid gap-4 sm:grid-cols-4">
                  <div>
                    <dt className="text-xs uppercase text-[var(--muted)]">Cohort</dt>
                    <dd className="mt-1 font-display text-2xl tabular-nums">
                      {analytics.data.retention.cohort}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase text-[var(--muted)]">D1</dt>
                    <dd className="mt-1 font-display text-2xl tabular-nums">
                      {(analytics.data.retention.d1 * 100).toFixed(1)}%
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase text-[var(--muted)]">D7</dt>
                    <dd className="mt-1 font-display text-2xl tabular-nums">
                      {(analytics.data.retention.d7 * 100).toFixed(1)}%
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase text-[var(--muted)]">D30</dt>
                    <dd className="mt-1 font-display text-2xl tabular-nums">
                      {(analytics.data.retention.d30 * 100).toFixed(1)}%
                    </dd>
                  </div>
                </dl>
              </Card>
            </>
          ) : analytics.isLoading ? (
            <p className="text-sm text-[var(--muted)]">{t("loading")}</p>
          ) : null}
        </div>
      ) : null}

      {tab === "growth" ? (
        <div className="mt-8 space-y-8">
          {growth.isError ? (
            <p className="text-[var(--color-danger)]" role="alert">
              {t("growthError")}
            </p>
          ) : null}
          {growth.data ? (
            <>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
                    {t("growthSearchImpressions")}
                  </p>
                  <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
                    {growth.data.search_impressions}
                  </p>
                </Card>
                <Card>
                  <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
                    {t("growthToolViews")}
                  </p>
                  <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
                    {growth.data.tool_views}
                  </p>
                </Card>
                <Card>
                  <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
                    {t("growthToolUsage")}
                  </p>
                  <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
                    {growth.data.tool_usage}
                  </p>
                </Card>
                <Card>
                  <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
                    {t("growthConversion")}
                  </p>
                  <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
                    {(growth.data.conversion_rate * 100).toFixed(2)}%
                  </p>
                </Card>
              </div>

              <Card>
                <h2 className="font-display text-lg font-semibold">
                  {t("growthReturning")}
                </h2>
                <dl className="mt-4 grid gap-4 sm:grid-cols-3">
                  <div>
                    <dt className="text-xs uppercase text-[var(--muted)]">
                      {t("growthActors")}
                    </dt>
                    <dd className="mt-1 font-display text-2xl tabular-nums">
                      {growth.data.returning_users.total_actors}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase text-[var(--muted)]">
                      {t("growthReturningActors")}
                    </dt>
                    <dd className="mt-1 font-display text-2xl tabular-nums">
                      {growth.data.returning_users.returning_actors}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase text-[var(--muted)]">
                      {t("growthReturningRate")}
                    </dt>
                    <dd className="mt-1 font-display text-2xl tabular-nums">
                      {(growth.data.returning_users.returning_rate * 100).toFixed(1)}%
                    </dd>
                  </div>
                </dl>
              </Card>

              <div className="grid gap-6 lg:grid-cols-2">
                <Card>
                  <h2 className="font-display text-lg font-semibold">
                    {t("growthLanguages")}
                  </h2>
                  <div className="mt-4 space-y-3">
                    {growth.data.languages.map((row) => (
                      <CssBar
                        key={row.locale}
                        label={row.locale}
                        value={row.count}
                        max={growthLangMax}
                      />
                    ))}
                    {growth.data.languages.length === 0 ? (
                      <p className="text-sm text-[var(--muted)]">{t("growthEmpty")}</p>
                    ) : null}
                  </div>
                </Card>
                <Card>
                  <h2 className="font-display text-lg font-semibold">
                    {t("growthSources")}
                  </h2>
                  <div className="mt-4 space-y-3">
                    {growth.data.traffic_sources.map((row) => (
                      <CssBar
                        key={row.host}
                        label={row.host}
                        value={row.count}
                        max={growthSourceMax}
                      />
                    ))}
                    {growth.data.traffic_sources.length === 0 ? (
                      <p className="text-sm text-[var(--muted)]">{t("growthEmpty")}</p>
                    ) : null}
                  </div>
                </Card>
              </div>
            </>
          ) : growth.isLoading ? (
            <p className="text-sm text-[var(--muted)]">{t("loading")}</p>
          ) : null}
        </div>
      ) : null}

      {tab === "apiKeys" ? (
        <div className="mt-8 space-y-6">
          <Card>
            <h2 className="font-display text-xl font-semibold">{t("apiKeysTitle")}</h2>
            <p className="mt-2 text-sm text-[var(--muted)]">{t("apiKeysNote")}</p>
            <Button asChild className="mt-4" variant="secondary">
              <Link href="/developers">{t("apiKeysCta")}</Link>
            </Button>
          </Card>
          {aiUsage.data ? (
            <Card>
              <h2 className="font-display text-lg font-semibold">{t("aiUsageSummary")}</h2>
              <p className="mt-2 text-sm text-[var(--muted)]">
                {t("aiTotalCalls")}:{" "}
                <span className="font-semibold text-[var(--foreground)] tabular-nums">
                  {aiUsage.data.total_calls}
                </span>
              </p>
            </Card>
          ) : null}
        </div>
      ) : null}

      {tab === "aiUsage" ? (
        <div className="mt-8 space-y-6">
          {aiUsage.isError ? (
            <p className="text-[var(--color-danger)]" role="alert">
              {t("aiUsageError")}
            </p>
          ) : null}
          {aiUsage.data ? (
            <>
              <Card>
                <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
                  {t("aiTotalCalls")}
                </p>
                <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
                  {aiUsage.data.total_calls}
                </p>
              </Card>
              <Card>
                <h2 className="font-display text-lg font-semibold">{t("aiByProvider")}</h2>
                <div className="mt-4 space-y-3">
                  {aiUsage.data.by_provider.map((row) => (
                    <div key={row.provider} className="space-y-1">
                      <CssBar
                        label={row.provider}
                        value={row.calls}
                        max={providerMax}
                      />
                      <p className="text-xs text-[var(--muted)]">
                        in {row.tokens_in ?? 0} · out {row.tokens_out ?? 0} · cost{" "}
                        {row.cost ?? 0}
                      </p>
                    </div>
                  ))}
                </div>
                {aiUsage.data.by_provider.length === 0 ? (
                  <p className="mt-4 text-sm text-[var(--muted)]">{t("aiUsageEmpty")}</p>
                ) : null}
              </Card>
            </>
          ) : aiUsage.isLoading ? (
            <p className="text-sm text-[var(--muted)]">{t("loading")}</p>
          ) : null}
        </div>
      ) : null}

      {tab === "factory" ? <AdminFactoryPanel /> : null}
      {tab === "seo" ? <AdminSeoPanel /> : null}
      {tab === "revenue" ? <AdminRevenuePanel /> : null}
      {tab === "toolsGrowth" ? <AdminToolsGrowthPanel /> : null}
      {tab === "content" ? <AdminContentPanel /> : null}
      {tab === "intelligence" ? <AdminIntelligencePanel /> : null}
      {tab === "keywords" ? <AdminKeywordsPanel /> : null}
      {tab === "autopilot" ? <AdminAutopilotPanel /> : null}
      {tab === "email" ? <AdminEmailPanel /> : null}
      {tab === "experiments" ? <AdminExperimentsPanel /> : null}
      {tab === "commandCenter" ? <AdminCommandCenterPanel /> : null}
      {tab === "toolScores" ? <AdminToolScoresPanel /> : null}
      {tab === "limits" ? <AdminLimitsPanel /> : null}
      {tab === "growthAgent" ? (
        <>
          <AdminGrowthAgentPanel />
          <AdminGrowthTasksSection />
        </>
      ) : null}
      {tab === "competitors" ? <AdminCompetitorsPanel /> : null}
      {tab === "backlinks" ? <AdminBacklinksPanel /> : null}
      {tab === "workflows" ? <AdminWorkflowsPanel /> : null}
      {tab === "moderation" ? <AdminModerationPanel /> : null}
      {tab === "creators" ? <AdminCreatorsPanel /> : null}
      {tab === "salesLeads" ? <AdminSalesLeadsPanel /> : null}
      {tab === "launchReadiness" ? <AdminLaunchReadinessPanel /> : null}
    </div>
  );
}

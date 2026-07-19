"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import {
  ApiError,
  api,
  type ContentItem,
  type SeoRecommendationItem,
  type ToolSpecItem,
} from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { localize } from "@/lib/utils";
import { AdminSeoHealthSection } from "./admin-scale-panels";
import { AdminSeoOpportunityTasksSection } from "./admin-gtm-panels";

const RECIPES = [
  "generic",
  "pdf",
  "image",
  "ai",
  "developer",
  "calculator",
] as const;

function asList<T>(data: T[] | { results: T[] } | undefined): T[] {
  if (!data) return [];
  return Array.isArray(data) ? data : data.results;
}

function AdminKeywordsSubPanel() {
  const t = useTranslations("admin");
  const keywords = useQuery({
    queryKey: ["admin-keywords-seo-sub"],
    queryFn: () => api.keywords.top(20),
    retry: false,
  });
  const list = asList(keywords.data);

  return (
    <section>
      <h3 className="font-display text-lg font-semibold">{t("keywordsTitle")}</h3>
      <p className="mt-1 text-sm text-[var(--muted)]">{t("keywordsSupporting")}</p>
      <ul className="mt-4 divide-y divide-[var(--border)] overflow-hidden rounded-[var(--radius-lg)] surface">
        {list.map((row) => (
          <li
            key={row.id}
            className="flex items-center justify-between gap-3 px-4 py-2 text-sm"
          >
            <span className="truncate font-medium">{row.keyword}</span>
            <span className="shrink-0 tabular-nums text-[var(--muted)]">
              vol {row.search_volume} · score {Number(row.priority_score).toFixed(1)}
            </span>
          </li>
        ))}
      </ul>
      {list.length === 0 && !keywords.isLoading ? (
        <p className="mt-3 text-sm text-[var(--muted)]">{t("keywordsEmpty")}</p>
      ) : null}
    </section>
  );
}

export function AdminFactoryPanel() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();
  const [slug, setSlug] = useState("");
  const [nameEn, setNameEn] = useState("");
  const [category, setCategory] = useState("ai");
  const [recipe, setRecipe] = useState<string>("generic");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const specs = useQuery({
    queryKey: ["admin-tool-specs"],
    queryFn: () => api.toolFactory.listSpecs(),
    retry: false,
  });

  const createMutation = useMutation({
    mutationFn: () =>
      api.toolFactory.createSpec({
        slug: slug.trim(),
        category_slug: category.trim(),
        name: { en: nameEn.trim() },
        description: { en: nameEn.trim() },
        recipe,
      }),
    onSuccess: async () => {
      setError(null);
      setSuccess(t("factoryCreated"));
      setSlug("");
      setNameEn("");
      await queryClient.invalidateQueries({ queryKey: ["admin-tool-specs"] });
    },
    onError: (err) => {
      setSuccess(null);
      setError(err instanceof ApiError ? err.message : t("factoryError"));
    },
  });

  const buildMutation = useMutation({
    mutationFn: (id: number) => api.toolFactory.buildSpec(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-tool-specs"] });
    },
  });

  const publishMutation = useMutation({
    mutationFn: (id: number) => api.toolFactory.publishSpec(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-tool-specs"] });
    },
  });

  const list = asList(specs.data);

  return (
    <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_1fr]">
      <Card>
        <h2 className="font-display text-xl font-semibold">{t("factoryTitle")}</h2>
        <p className="mt-1 text-sm text-[var(--muted)]">{t("factorySupporting")}</p>
        <form
          className="mt-6 space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            setError(null);
            setSuccess(null);
            createMutation.mutate();
          }}
        >
          <div>
            <Label htmlFor="factory-slug">{t("factorySlug")}</Label>
            <Input
              id="factory-slug"
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
              placeholder="my-tool"
              required
            />
          </div>
          <div>
            <Label htmlFor="factory-name">{t("factoryName")}</Label>
            <Input
              id="factory-name"
              value={nameEn}
              onChange={(e) => setNameEn(e.target.value)}
              placeholder="My Tool"
              required
            />
          </div>
          <div>
            <Label htmlFor="factory-category">{t("factoryCategory")}</Label>
            <Input
              id="factory-category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="ai"
              required
            />
          </div>
          <div>
            <Label htmlFor="factory-recipe">{t("factoryRecipe")}</Label>
            <select
              id="factory-recipe"
              className="flex h-10 w-full rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--card)] px-3 text-sm"
              value={recipe}
              onChange={(e) => setRecipe(e.target.value)}
            >
              {RECIPES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
          {error ? (
            <p className="text-sm text-[var(--color-danger)]" role="alert">
              {error}
            </p>
          ) : null}
          {success ? (
            <p className="text-sm text-[var(--accent)]">{success}</p>
          ) : null}
          <Button type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending ? t("factorySaving") : t("factoryCreate")}
          </Button>
        </form>
      </Card>

      <div>
        <h2 className="font-display text-xl font-semibold">{t("factoryList")}</h2>
        {specs.isLoading ? (
          <p className="mt-4 text-sm text-[var(--muted)]">{t("loading")}</p>
        ) : null}
        {specs.isError ? (
          <p className="mt-4 text-sm text-[var(--color-danger)]">{t("factoryError")}</p>
        ) : null}
        <ul className="mt-4 space-y-3">
          {list.map((spec: ToolSpecItem) => {
            const title =
              typeof spec.name === "string"
                ? spec.name
                : localize(spec.name, "en");
            return (
              <li key={spec.id} className="surface rounded-[var(--radius-lg)] p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="font-medium">{title}</p>
                    <p className="mt-1 font-mono text-xs text-[var(--muted)]">
                      {spec.slug} · {spec.recipe} · {spec.status}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      disabled={buildMutation.isPending}
                      onClick={() => buildMutation.mutate(spec.id)}
                    >
                      {buildMutation.isPending
                        ? t("factoryBuilding")
                        : t("factoryBuild")}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      disabled={
                        publishMutation.isPending || spec.status === "published"
                      }
                      onClick={() => publishMutation.mutate(spec.id)}
                    >
                      {t("factoryPublish")}
                    </Button>
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
        {list.length === 0 && !specs.isLoading ? (
          <p className="mt-4 text-sm text-[var(--muted)]">{t("factoryEmpty")}</p>
        ) : null}
      </div>
    </div>
  );
}

export function AdminSeoPanel() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();
  const [analyzePath, setAnalyzePath] = useState("/");

  const gsc = useQuery({
    queryKey: ["admin-gsc-overview"],
    queryFn: () => api.gsc.overview(28),
    retry: false,
  });

  const recommendations = useQuery({
    queryKey: ["admin-seo-recommendations"],
    queryFn: () => api.seo.recommendations({ status: "open" }),
    retry: false,
  });

  const issues = useQuery({
    queryKey: ["admin-seo-issues"],
    queryFn: () => api.seo.listIssues({ status: "open" }),
    retry: false,
  });

  const analyzeMutation = useMutation({
    mutationFn: () => api.seo.analyze(analyzePath.trim()),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["admin-seo-recommendations"],
      });
    },
  });

  const scanAutopilot = useMutation({
    mutationFn: () => api.seo.scanAutopilot(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-seo-issues"] });
    },
  });

  const acceptMutation = useMutation({
    mutationFn: (id: number) => api.seo.acceptRec(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["admin-seo-recommendations"],
      });
    },
  });

  const dismissMutation = useMutation({
    mutationFn: (id: number) => api.seo.dismissRec(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["admin-seo-recommendations"],
      });
    },
  });

  const applyIssue = useMutation({
    mutationFn: (id: number) => api.seo.applyIssue(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-seo-issues"] });
    },
  });

  const dismissIssue = useMutation({
    mutationFn: (id: number) => api.seo.dismissIssue(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-seo-issues"] });
    },
  });

  const recs = asList(recommendations.data);
  const issueList = asList(issues.data);

  return (
    <div className="mt-8 space-y-8">
      <h2 className="font-display text-xl font-semibold">{t("seoTitle")}</h2>
      {gsc.isError || recommendations.isError ? (
        <p className="text-[var(--color-danger)]" role="alert">
          {t("seoError")}
        </p>
      ) : null}

      {gsc.data ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
              {t("seoGscClicks")}
            </p>
            <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
              {gsc.data.clicks}
            </p>
          </Card>
          <Card>
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
              {t("seoGscImpressions")}
            </p>
            <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
              {gsc.data.impressions}
            </p>
          </Card>
          <Card>
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
              {t("seoGscCtr")}
            </p>
            <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
              {(Number(gsc.data.avg_ctr) * 100).toFixed(2)}%
            </p>
          </Card>
          <Card>
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
              {t("seoGscPosition")}
            </p>
            <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
              {Number(gsc.data.avg_position).toFixed(1)}
            </p>
          </Card>
        </div>
      ) : gsc.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("loading")}</p>
      ) : null}

      <Card>
        <form
          className="flex flex-wrap items-end gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            analyzeMutation.mutate();
          }}
        >
          <div className="min-w-[240px] flex-1">
            <Label htmlFor="seo-path">{t("seoAnalyzePath")}</Label>
            <Input
              id="seo-path"
              value={analyzePath}
              onChange={(e) => setAnalyzePath(e.target.value)}
              placeholder="/tools/ai/example"
              required
            />
          </div>
          <Button type="submit" disabled={analyzeMutation.isPending}>
            {analyzeMutation.isPending ? t("seoAnalyzing") : t("seoAnalyze")}
          </Button>
        </form>
        {analyzeMutation.isError ? (
          <p className="mt-3 text-sm text-[var(--color-danger)]" role="alert">
            {analyzeMutation.error instanceof ApiError
              ? analyzeMutation.error.message
              : t("seoError")}
          </p>
        ) : null}
      </Card>

      <AdminKeywordsSubPanel />

      <AdminSeoHealthSection />

      <AdminSeoOpportunityTasksSection />

      <section>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h3 className="font-display text-lg font-semibold">
              {t("seoAutopilotIssues")}
            </h3>
            <p className="mt-1 text-sm text-[var(--muted)]">
              {t("seoAutopilotSupporting")}
            </p>
          </div>
          <Button
            type="button"
            size="sm"
            variant="secondary"
            disabled={scanAutopilot.isPending}
            onClick={() => scanAutopilot.mutate()}
          >
            {scanAutopilot.isPending
              ? t("seoAutopilotScanning")
              : t("seoAutopilotScan")}
          </Button>
        </div>
        {scanAutopilot.isError ? (
          <p className="mt-3 text-sm text-[var(--color-danger)]" role="alert">
            {scanAutopilot.error instanceof ApiError
              ? scanAutopilot.error.message
              : t("seoError")}
          </p>
        ) : null}
        <ul className="mt-4 space-y-3">
          {issueList.map((issue) => (
            <li key={issue.id} className="surface rounded-[var(--radius-lg)] p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <p className="font-mono text-xs text-[var(--muted)]">
                    {issue.path} · {issue.issue_type} · {issue.severity}
                  </p>
                  <p className="mt-2 text-sm">{issue.suggestion}</p>
                </div>
                {issue.status === "open" ? (
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      size="sm"
                      disabled={applyIssue.isPending}
                      onClick={() => applyIssue.mutate(issue.id)}
                    >
                      {t("seoApplyIssue")}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      disabled={dismissIssue.isPending}
                      onClick={() => dismissIssue.mutate(issue.id)}
                    >
                      {t("seoDismissIssue")}
                    </Button>
                  </div>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
        {issueList.length === 0 && !issues.isLoading ? (
          <p className="mt-4 text-sm text-[var(--muted)]">
            {t("seoAutopilotEmpty")}
          </p>
        ) : null}
      </section>

      <section>
        <h3 className="font-display text-lg font-semibold">
          {t("seoRecommendations")}
        </h3>
        <ul className="mt-4 space-y-3">
          {recs.map((rec: SeoRecommendationItem) => (
            <li key={rec.id} className="surface rounded-[var(--radius-lg)] p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <p className="font-mono text-xs text-[var(--muted)]">
                    {rec.path} · {rec.type} · {rec.severity}
                  </p>
                  <p className="mt-2 text-sm">{rec.suggestion}</p>
                  {rec.rationale ? (
                    <p className="mt-1 text-xs text-[var(--muted)]">{rec.rationale}</p>
                  ) : null}
                </div>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    size="sm"
                    disabled={acceptMutation.isPending}
                    onClick={() => acceptMutation.mutate(rec.id)}
                  >
                    {t("seoAccept")}
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="secondary"
                    disabled={dismissMutation.isPending}
                    onClick={() => dismissMutation.mutate(rec.id)}
                  >
                    {t("seoDismiss")}
                  </Button>
                </div>
              </div>
            </li>
          ))}
        </ul>
        {recs.length === 0 && !recommendations.isLoading ? (
          <p className="mt-4 text-sm text-[var(--muted)]">{t("seoEmpty")}</p>
        ) : null}
      </section>
    </div>
  );
}

export function AdminRevenuePanel() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();

  const summary = useQuery({
    queryKey: ["admin-revenue-summary"],
    queryFn: () => api.adminRevenue.summary(),
    retry: false,
  });

  const placements = useQuery({
    queryKey: ["admin-revenue-placements"],
    queryFn: () => api.adminRevenue.placements(),
    retry: false,
  });

  const adPerf = useQuery({
    queryKey: ["admin-ad-performance"],
    queryFn: () => api.revenue.adPerformance(),
    retry: false,
  });

  const adRecs = useQuery({
    queryKey: ["admin-ad-recommendations"],
    queryFn: () => api.revenue.adRecommendations({ status: "open" }),
    retry: false,
  });

  const generateRecs = useMutation({
    mutationFn: () => api.revenue.generateAdRecommendations(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["admin-ad-recommendations"],
      });
    },
  });

  const acceptRec = useMutation({
    mutationFn: (id: number) => api.revenue.acceptAdRec(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["admin-ad-recommendations"],
      });
    },
  });

  const dismissRec = useMutation({
    mutationFn: (id: number) => api.revenue.dismissAdRec(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["admin-ad-recommendations"],
      });
    },
  });

  const cents = summary.data?.total_cents ?? 0;
  const perfList = asList(adPerf.data);
  const recList = asList(adRecs.data);

  return (
    <div className="mt-8 space-y-8">
      <h2 className="font-display text-xl font-semibold">{t("revenueTitle")}</h2>
      {summary.isError || placements.isError ? (
        <p className="text-[var(--color-danger)]" role="alert">
          {t("revenueError")}
        </p>
      ) : null}

      {summary.data ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Card>
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
              {t("revenueTotal")}
            </p>
            <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
              ${(cents / 100).toFixed(2)}
            </p>
          </Card>
          <Card>
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
              {t("revenueEvents")}
            </p>
            <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
              {summary.data.event_count}
            </p>
          </Card>
          <Card>
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
              {t("revenuePlacements")}
            </p>
            <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
              {summary.data.placements}
            </p>
          </Card>
          <Card>
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
              {t("revenueSponsored")}
            </p>
            <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
              {summary.data.sponsored_active}
            </p>
          </Card>
          <Card>
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
              {t("revenueAffiliates")}
            </p>
            <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
              {summary.data.affiliates_active}
            </p>
          </Card>
        </div>
      ) : summary.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("loading")}</p>
      ) : null}

      <section>
        <h3 className="font-display text-lg font-semibold">
          {t("revenuePlacementsList")}
        </h3>
        <ul className="mt-4 divide-y divide-[var(--border)] surface overflow-hidden rounded-[var(--radius-lg)]">
          {(placements.data ?? []).map((p) => (
            <li
              key={p.id}
              className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm"
            >
              <span className="font-mono">{p.key}</span>
              <span className="text-[var(--muted)]">
                {p.network} · {p.enabled ? "on" : "off"}
              </span>
            </li>
          ))}
        </ul>
        {(placements.data ?? []).length === 0 && !placements.isLoading ? (
          <p className="mt-4 text-sm text-[var(--muted)]">{t("revenueEmpty")}</p>
        ) : null}
      </section>

      <section>
        <h3 className="font-display text-lg font-semibold">
          {t("revenueAdPerformance")}
        </h3>
        <ul className="mt-4 divide-y divide-[var(--border)] overflow-hidden rounded-[var(--radius-lg)] surface">
          {perfList.slice(0, 30).map((row) => (
            <li
              key={row.id}
              className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm"
            >
              <span className="font-mono text-xs">
                {row.date} · {row.placement_key}
              </span>
              <span className="text-[var(--muted)]">
                {row.impressions} imp · {row.clicks} clk · $
                {(Number(row.revenue_cents) / 100).toFixed(2)}
              </span>
            </li>
          ))}
        </ul>
        {perfList.length === 0 && !adPerf.isLoading ? (
          <p className="mt-4 text-sm text-[var(--muted)]">
            {t("revenueAdPerformanceEmpty")}
          </p>
        ) : null}
      </section>

      <section>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h3 className="font-display text-lg font-semibold">
              {t("revenueAdRecs")}
            </h3>
            <p className="mt-1 text-sm text-[var(--muted)]">
              {t("revenueAdRecsSupporting")}
            </p>
          </div>
          <Button
            type="button"
            size="sm"
            variant="secondary"
            disabled={generateRecs.isPending}
            onClick={() => generateRecs.mutate()}
          >
            {generateRecs.isPending
              ? t("revenueAdRecsGenerating")
              : t("revenueAdRecsGenerate")}
          </Button>
        </div>
        <ul className="mt-4 space-y-3">
          {recList.map((rec) => (
            <li key={rec.id} className="surface rounded-[var(--radius-lg)] p-4 text-sm">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-medium">{rec.title}</p>
                  <p className="mt-1 text-xs text-[var(--muted)]">
                    {rec.placement_key} · priority {rec.priority} · {rec.status}
                  </p>
                  {rec.rationale ? (
                    <p className="mt-2 text-[var(--muted)]">{rec.rationale}</p>
                  ) : null}
                </div>
                {rec.status === "open" ? (
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      size="sm"
                      disabled={acceptRec.isPending}
                      onClick={() => acceptRec.mutate(rec.id)}
                    >
                      {t("revenueAdRecAccept")}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      disabled={dismissRec.isPending}
                      onClick={() => dismissRec.mutate(rec.id)}
                    >
                      {t("revenueAdRecDismiss")}
                    </Button>
                  </div>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
        {recList.length === 0 && !adRecs.isLoading ? (
          <p className="mt-4 text-sm text-[var(--muted)]">
            {t("revenueAdRecsEmpty")}
          </p>
        ) : null}
      </section>
    </div>
  );
}

export function AdminToolsGrowthPanel() {
  const t = useTranslations("admin");

  const growth = useQuery({
    queryKey: ["admin-tools-growth"],
    queryFn: () => api.toolsGrowth(),
    retry: false,
  });

  const cats = growth.data?.categories ?? [];
  const maxCount = Math.max(1, ...cats.map((c) => c.tool_count ?? 0));

  return (
    <div className="mt-8 space-y-8">
      <h2 className="font-display text-xl font-semibold">{t("toolsGrowthTitle")}</h2>
      {growth.isError ? (
        <p className="text-[var(--color-danger)]" role="alert">
          {t("toolsGrowthError")}
        </p>
      ) : null}

      {growth.data ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            <Card>
              <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
                {t("toolsGrowthTotal")}
              </p>
              <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
                {growth.data.metrics.tools}
              </p>
            </Card>
            <Card>
              <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
                {t("toolsGrowthPremium")}
              </p>
              <p className="mt-2 font-display text-3xl font-semibold tabular-nums">
                {growth.data.metrics.premium_tools}
              </p>
            </Card>
          </div>

          <Card>
            <div className="space-y-3">
              {cats.map((cat) => {
                const count = cat.tool_count ?? 0;
                const pct = Math.max(2, Math.round((count / maxCount) * 100));
                const label =
                  typeof cat.name === "string"
                    ? cat.name
                    : localize(cat.name, "en");
                return (
                  <div key={cat.id} className="space-y-1">
                    <div className="flex items-center justify-between gap-2 text-sm">
                      <span className="truncate">{label}</span>
                      <span className="tabular-nums text-[var(--muted)]">
                        {count}
                      </span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-[color-mix(in_oklab,var(--foreground)_8%,transparent)]">
                      <div
                        className="h-full rounded-full bg-[var(--accent)]"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
              {cats.length === 0 ? (
                <p className="text-sm text-[var(--muted)]">{t("toolsGrowthEmpty")}</p>
              ) : null}
            </div>
          </Card>
        </>
      ) : growth.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("loading")}</p>
      ) : null}
    </div>
  );
}

export function AdminContentPanel() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();

  const content = useQuery({
    queryKey: ["admin-content-list"],
    queryFn: () => api.contentList(),
    retry: false,
  });

  const publishMutation = useMutation({
    mutationFn: (id: number) => api.contentPublish(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-content-list"] });
    },
  });

  const items = asList(content.data);

  return (
    <div className="mt-8 space-y-6">
      <h2 className="font-display text-xl font-semibold">{t("contentTitle")}</h2>
      {content.isError ? (
        <p className="text-[var(--color-danger)]" role="alert">
          {t("contentError")}
        </p>
      ) : null}
      {content.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("loading")}</p>
      ) : null}
      <ul className="space-y-3">
        {items.map((item: ContentItem) => (
          <li key={item.id} className="surface rounded-[var(--radius-lg)] p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="font-medium">{item.title || item.slug}</p>
                <p className="mt-1 font-mono text-xs text-[var(--muted)]">
                  {item.slug} · {t("contentStatus")}: {item.status} ·{" "}
                  {item.content_type}
                </p>
              </div>
              {item.status !== "published" ? (
                <Button
                  type="button"
                  size="sm"
                  disabled={publishMutation.isPending}
                  onClick={() => publishMutation.mutate(item.id)}
                >
                  {publishMutation.isPending
                    ? t("contentPublishing")
                    : t("contentPublish")}
                </Button>
              ) : null}
            </div>
          </li>
        ))}
      </ul>
      {items.length === 0 && !content.isLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("contentEmpty")}</p>
      ) : null}
    </div>
  );
}

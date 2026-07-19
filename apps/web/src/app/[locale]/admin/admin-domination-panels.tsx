"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { ApiError, api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

function asList<T>(data: T[] | { results: T[] } | undefined): T[] {
  if (!data) return [];
  return Array.isArray(data) ? data : data.results;
}

export function AdminCompetitorsPanel() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();
  const [domain, setDomain] = useState("");
  const [name, setName] = useState("");

  const domains = useQuery({
    queryKey: ["admin-competitor-domains"],
    queryFn: () => api.competitors.listDomains(),
    retry: false,
  });

  const opportunities = useQuery({
    queryKey: ["admin-competitor-opportunities"],
    queryFn: () => api.competitors.listOpportunities({ status: "open" }),
    retry: false,
  });

  const createDomain = useMutation({
    mutationFn: () =>
      api.competitors.createDomain({
        domain: domain.trim(),
        name: name.trim() || domain.trim(),
      }),
    onSuccess: async () => {
      setDomain("");
      setName("");
      await queryClient.invalidateQueries({
        queryKey: ["admin-competitor-domains"],
      });
    },
  });

  const recompute = useMutation({
    mutationFn: () => api.competitors.recompute(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["admin-competitor-opportunities"],
      });
    },
  });

  const domainList = asList(domains.data);
  const oppList = asList(opportunities.data);

  return (
    <div className="mt-8 space-y-8">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="font-display text-xl font-semibold">
            {t("competitorsTitle")}
          </h2>
          <p className="mt-1 text-sm text-[var(--muted)]">
            {t("competitorsSupporting")}
          </p>
        </div>
        <Button
          type="button"
          size="sm"
          variant="secondary"
          disabled={recompute.isPending}
          onClick={() => recompute.mutate()}
        >
          {recompute.isPending
            ? t("competitorsRecomputing")
            : t("competitorsRecompute")}
        </Button>
      </div>

      {(domains.isError || opportunities.isError || createDomain.isError) && (
        <p className="text-sm text-[var(--color-danger)]" role="alert">
          {createDomain.error instanceof ApiError
            ? createDomain.error.message
            : t("competitorsError")}
        </p>
      )}

      <form
        className="flex flex-wrap items-end gap-3"
        onSubmit={(e) => {
          e.preventDefault();
          createDomain.mutate();
        }}
      >
        <div className="min-w-[180px] flex-1">
          <Label htmlFor="competitor-domain">{t("competitorsDomain")}</Label>
          <Input
            id="competitor-domain"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder="example.com"
            required
          />
        </div>
        <div className="min-w-[180px] flex-1">
          <Label htmlFor="competitor-name">{t("competitorsName")}</Label>
          <Input
            id="competitor-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Display name"
          />
        </div>
        <Button type="submit" disabled={createDomain.isPending || !domain.trim()}>
          {t("competitorsAdd")}
        </Button>
      </form>

      <section>
        <h3 className="font-display text-lg font-semibold">
          {t("competitorsDomains")}
        </h3>
        <ul className="mt-4 divide-y divide-[var(--border)] overflow-hidden rounded-[var(--radius-lg)] surface">
          {domainList.map((row) => (
            <li
              key={row.id}
              className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm"
            >
              <span className="font-mono text-xs">{row.domain}</span>
              <span className="text-[var(--muted)]">
                {row.name || "—"} · {row.is_active ? "active" : "off"}
              </span>
            </li>
          ))}
        </ul>
        {domainList.length === 0 && !domains.isLoading ? (
          <p className="mt-4 text-sm text-[var(--muted)]">
            {t("competitorsDomainsEmpty")}
          </p>
        ) : null}
      </section>

      <section>
        <h3 className="font-display text-lg font-semibold">
          {t("competitorsOpportunities")}
        </h3>
        <ul className="mt-4 space-y-3">
          {oppList.map((opp) => (
            <li key={opp.id} className="surface rounded-[var(--radius-lg)] p-4 text-sm">
              <p className="font-medium">{opp.title || opp.keyword}</p>
              <p className="mt-1 text-xs text-[var(--muted)]">
                {opp.competitor_domain} · gap {opp.gap_score} · {opp.status}
              </p>
              {opp.rationale ? (
                <p className="mt-2 text-[var(--muted)]">{opp.rationale}</p>
              ) : null}
            </li>
          ))}
        </ul>
        {oppList.length === 0 && !opportunities.isLoading ? (
          <p className="mt-4 text-sm text-[var(--muted)]">
            {t("competitorsOpportunitiesEmpty")}
          </p>
        ) : null}
      </section>
    </div>
  );
}

export function AdminBacklinksPanel() {
  const t = useTranslations("admin");
  const queryClient = useQueryClient();

  const targets = useQuery({
    queryKey: ["admin-backlink-targets"],
    queryFn: () => api.backlinks.listTargets(),
    retry: false,
  });

  const campaigns = useQuery({
    queryKey: ["admin-backlink-campaigns"],
    queryFn: () => api.backlinks.listCampaigns(),
    retry: false,
  });

  const opportunities = useQuery({
    queryKey: ["admin-backlink-opportunities"],
    queryFn: () => api.backlinks.listOpportunities(),
    retry: false,
  });

  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      api.backlinks.updateOpportunityStatus(id, status),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["admin-backlink-opportunities"],
      });
    },
  });

  const targetList = asList(targets.data);
  const campaignList = asList(campaigns.data);
  const oppList = asList(opportunities.data);

  return (
    <div className="mt-8 space-y-8">
      <div>
        <h2 className="font-display text-xl font-semibold">
          {t("backlinksTitle")}
        </h2>
        <p className="mt-1 text-sm text-[var(--muted)]">
          {t("backlinksSupporting")}
        </p>
      </div>

      {(targets.isError || campaigns.isError || opportunities.isError) && (
        <p className="text-sm text-[var(--color-danger)]" role="alert">
          {t("backlinksError")}
        </p>
      )}

      <section>
        <h3 className="font-display text-lg font-semibold">
          {t("backlinksTargets")}
        </h3>
        <ul className="mt-4 divide-y divide-[var(--border)] overflow-hidden rounded-[var(--radius-lg)] surface">
          {targetList.map((row) => (
            <li key={row.id} className="px-4 py-3 text-sm">
              <p className="font-medium">{row.title || row.path || row.url}</p>
              <p className="mt-1 font-mono text-xs text-[var(--muted)]">
                {row.url || row.path}
              </p>
            </li>
          ))}
        </ul>
        {targetList.length === 0 && !targets.isLoading ? (
          <p className="mt-4 text-sm text-[var(--muted)]">
            {t("backlinksTargetsEmpty")}
          </p>
        ) : null}
      </section>

      <section>
        <h3 className="font-display text-lg font-semibold">
          {t("backlinksCampaigns")}
        </h3>
        <ul className="mt-4 divide-y divide-[var(--border)] overflow-hidden rounded-[var(--radius-lg)] surface">
          {campaignList.map((row) => (
            <li
              key={row.id}
              className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm"
            >
              <span className="font-medium">{row.name}</span>
              <span className="text-[var(--muted)]">{row.status}</span>
            </li>
          ))}
        </ul>
        {campaignList.length === 0 && !campaigns.isLoading ? (
          <p className="mt-4 text-sm text-[var(--muted)]">
            {t("backlinksCampaignsEmpty")}
          </p>
        ) : null}
      </section>

      <section>
        <h3 className="font-display text-lg font-semibold">
          {t("backlinksOpportunities")}
        </h3>
        <ul className="mt-4 space-y-3">
          {oppList.map((opp) => (
            <li key={opp.id} className="surface rounded-[var(--radius-lg)] p-4 text-sm">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-medium">
                    {opp.source_domain || opp.source_url || `#${opp.id}`}
                  </p>
                  <p className="mt-1 text-xs text-[var(--muted)]">
                    priority {opp.priority} · {opp.status}
                  </p>
                  {opp.rationale ? (
                    <p className="mt-2 text-[var(--muted)]">{opp.rationale}</p>
                  ) : null}
                </div>
                {opp.status === "open" ? (
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      size="sm"
                      disabled={updateStatus.isPending}
                      onClick={() =>
                        updateStatus.mutate({ id: opp.id, status: "outreach" })
                      }
                    >
                      {t("backlinksOutreach")}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      disabled={updateStatus.isPending}
                      onClick={() =>
                        updateStatus.mutate({ id: opp.id, status: "dismissed" })
                      }
                    >
                      {t("backlinksDismiss")}
                    </Button>
                  </div>
                ) : null}
                {opp.status === "outreach" ? (
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      size="sm"
                      disabled={updateStatus.isPending}
                      onClick={() =>
                        updateStatus.mutate({ id: opp.id, status: "won" })
                      }
                    >
                      {t("backlinksWon")}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      disabled={updateStatus.isPending}
                      onClick={() =>
                        updateStatus.mutate({ id: opp.id, status: "lost" })
                      }
                    >
                      {t("backlinksLost")}
                    </Button>
                  </div>
                ) : null}
              </div>
              {updateStatus.isError && updateStatus.variables?.id === opp.id ? (
                <p className="mt-2 text-xs text-[var(--color-danger)]" role="alert">
                  {updateStatus.error instanceof ApiError
                    ? updateStatus.error.message
                    : t("backlinksError")}
                </p>
              ) : null}
            </li>
          ))}
        </ul>
        {oppList.length === 0 && !opportunities.isLoading ? (
          <p className="mt-4 text-sm text-[var(--muted)]">
            {t("backlinksOpportunitiesEmpty")}
          </p>
        ) : null}
      </section>
    </div>
  );
}

"use client";

import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

export function SponsoredBadge({
  toolId,
  toolSlug,
  className,
}: {
  toolId?: string;
  toolSlug?: string;
  className?: string;
}) {
  const t = useTranslations("sponsored");

  const query = useQuery({
    queryKey: ["monetization-sponsored"],
    queryFn: () => api.monetization.sponsored(),
    staleTime: 5 * 60_000,
    retry: false,
  });

  const match = (query.data ?? []).find((item) => {
    if (!item.is_active) return false;
    if (toolSlug && item.tool_slug === toolSlug) return true;
    if (toolId && (String(item.tool) === toolId || item.tool_slug === toolId)) {
      return true;
    }
    return false;
  });

  if (!match) return null;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-[var(--radius-md)] border border-[var(--border)] bg-[color-mix(in_oklab,var(--accent)_10%,transparent)] px-2.5 py-1 text-xs font-medium text-[var(--accent)]",
        className,
      )}
      title={match.sponsor_name}
    >
      {t("badge")}
      <span className="text-[var(--muted)]">· {match.sponsor_name}</span>
    </span>
  );
}

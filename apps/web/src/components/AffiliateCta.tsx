"use client";

import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { api, type AffiliateLinkItem } from "@/lib/api";
import { cn } from "@/lib/utils";

function withUtm(url: string, utm: Record<string, unknown>): string {
  try {
    const parsed = new URL(url);
    for (const [key, value] of Object.entries(utm)) {
      if (value !== undefined && value !== null && String(value)) {
        parsed.searchParams.set(key, String(value));
      }
    }
    return parsed.toString();
  } catch {
    return url;
  }
}

function filterAffiliates(
  items: AffiliateLinkItem[],
  toolId?: string,
  toolSlug?: string,
): AffiliateLinkItem[] {
  return items.filter((item) => {
    if (!item.is_active) return false;
    if (toolSlug && item.tool_slug) return item.tool_slug === toolSlug;
    if (toolId && item.tool != null) {
      return String(item.tool) === toolId || item.tool_slug === toolId;
    }
    if (toolSlug || toolId) return !item.tool_slug && item.tool == null;
    return true;
  });
}

export function AffiliateCta({
  toolId,
  toolSlug,
  className,
}: {
  toolId?: string;
  toolSlug?: string;
  className?: string;
}) {
  const t = useTranslations("affiliate");

  const query = useQuery({
    queryKey: ["monetization-affiliates", toolId, toolSlug],
    queryFn: async () => {
      // Fetch all active links; filter client-side so string tool_id / slug both work.
      const list = await api.monetization.affiliates();
      return filterAffiliates(list, toolId, toolSlug);
    },
    enabled: Boolean(toolId || toolSlug),
    staleTime: 5 * 60_000,
    retry: false,
  });

  const links = query.data ?? [];
  if (!links.length) return null;

  return (
    <aside
      className={cn(
        "surface rounded-[var(--radius-lg)] p-4",
        className,
      )}
      aria-label={t("label")}
    >
      <p className="text-xs uppercase tracking-wider text-[var(--muted)]">
        {t("heading")}
      </p>
      <ul className="mt-3 space-y-2">
        {links.map((link) => (
          <li key={link.id}>
            <a
              href={withUtm(link.destination_url, link.utm ?? {})}
              target="_blank"
              rel="noopener noreferrer sponsored"
              className="block rounded-[var(--radius-md)] px-3 py-2 text-sm text-[var(--accent)] transition hover:bg-[color-mix(in_oklab,var(--accent)_10%,transparent)]"
            >
              {link.label}
              {link.network ? (
                <span className="ms-2 text-xs text-[var(--muted)]">
                  {link.network}
                </span>
              ) : null}
            </a>
          </li>
        ))}
      </ul>
    </aside>
  );
}

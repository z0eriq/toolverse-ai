"use client";

import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { useAuth } from "@/features/auth/auth-context";
import { api, type AdPlacementItem } from "@/lib/api";
import { cn, isAdsEnabled } from "@/lib/utils";

type Slot = "in-tool" | "sidebar" | "banner" | "satellite";

const heights: Record<Slot, string> = {
  banner: "min-h-[90px]",
  "in-tool": "min-h-[250px]",
  sidebar: "min-h-[280px]",
  satellite: "min-h-[120px]",
};

function placementForSlot(
  placements: AdPlacementItem[] | undefined,
  slot: Slot,
): AdPlacementItem | null {
  if (!placements?.length) return null;
  return placements.find((p) => p.key === slot) ?? null;
}

/**
 * Reserves AdSense layout space; prefers API placements, falls back to env adsense.
 */
export function AdSlot({
  slot = "banner",
  className,
  fetchPlacements = true,
}: {
  slot?: Slot;
  className?: string;
  /** When true, loads placement config from monetization API. */
  fetchPlacements?: boolean;
}) {
  const t = useTranslations("ads");
  const { user } = useAuth();
  const envEnabled = isAdsEnabled();

  const placements = useQuery({
    queryKey: ["monetization-placements"],
    queryFn: () => api.monetization.placements(),
    enabled: fetchPlacements,
    staleTime: 5 * 60_000,
    retry: false,
  });

  const placement = placementForSlot(placements.data, slot);
  const apiDisabled = placement !== null && !placement.enabled;
  const showAdsense =
    !apiDisabled &&
    (placement
      ? placement.network === "adsense" && placement.enabled
      : envEnabled);
  const customHtml =
    placement?.network === "custom" && placement.enabled
      ? String(placement.config.html ?? placement.config.content ?? "")
      : "";
  const customHref =
    placement?.network === "custom" && placement.enabled
      ? String(placement.config.href ?? placement.config.url ?? "")
      : "";
  const adClient =
    String(placement?.config.client ?? process.env.NEXT_PUBLIC_ADSENSE_CLIENT ?? "") ||
    undefined;
  const adSlotId = String(
    placement?.config.ad_slot ?? placement?.config.slot ?? slot,
  );

  // Pro (premium) subscribers are ads-free
  if (user?.is_premium) return null;
  if (apiDisabled) return null;

  return (
    <aside
      className={cn(
        "surface relative flex w-full items-center justify-center overflow-hidden rounded-[var(--radius-lg)]",
        heights[slot],
        className,
      )}
      aria-label={t("label")}
      data-ad-slot={slot}
      data-ad-network={placement?.network ?? (envEnabled ? "adsense" : "none")}
    >
      {customHtml ? (
        <div
          className="w-full p-3 text-sm"
          dangerouslySetInnerHTML={{ __html: customHtml }}
        />
      ) : customHref ? (
        <a
          href={customHref}
          target="_blank"
          rel="noopener noreferrer sponsored"
          className="px-4 text-sm text-[var(--accent)] hover:underline"
        >
          {String(placement?.config.label ?? t("label"))}
        </a>
      ) : showAdsense && adClient ? (
        <ins
          className="adsbygoogle block w-full"
          style={{ display: "block" }}
          data-ad-client={adClient}
          data-ad-slot={adSlotId}
          data-ad-format="auto"
          data-full-width-responsive="true"
        />
      ) : (
        <span className="text-xs text-[var(--muted)]">{t("label")}</span>
      )}
    </aside>
  );
}

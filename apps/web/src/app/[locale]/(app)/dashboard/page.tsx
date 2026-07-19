"use client";

import { useQuery } from "@tanstack/react-query";
import { useLocale, useTranslations } from "next-intl";
import { api } from "@/lib/api";
import { useAuth } from "@/features/auth/auth-context";
import { ToolCard } from "@/components/ToolCard";
import { Link } from "@/i18n/navigation";
import { Button } from "@/components/ui/button";
import { localize } from "@/lib/utils";
import { GamificationReferralStrip } from "@/components/GamificationReferralStrip";

function asLocalized(value: string | Record<string, string>) {
  if (typeof value === "string") return value;
  return {
    en: value.en ?? Object.values(value)[0] ?? "",
    ar: value.ar,
  };
}

export default function DashboardPage() {
  const t = useTranslations("dashboard");
  const locale = useLocale();
  const { user, isLoading: authLoading } = useAuth();

  const favorites = useQuery({
    queryKey: ["favorites"],
    queryFn: () => api.favorites(),
    enabled: Boolean(user),
  });

  const history = useQuery({
    queryKey: ["history"],
    queryFn: () => api.history(),
    enabled: Boolean(user),
  });

  if (authLoading) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <p className="text-[var(--muted)]">…</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h1 className="font-display text-3xl font-semibold">{t("title")}</h1>
        <p className="mt-2 text-[var(--muted)]">{t("supporting")}</p>
        <Button asChild className="mt-6">
          <Link href="/auth/login">Log in</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-12 px-4 py-16 sm:px-6">
      <div>
        <h1 className="font-display text-3xl font-semibold tracking-tight">{t("title")}</h1>
        <p className="mt-2 text-[var(--muted)]">
          {t("supporting")} · {user.email}
        </p>
      </div>

      <GamificationReferralStrip />

      <section>
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="font-display text-xl font-semibold">{t("favorites")}</h2>
          <Link href="/favorites" className="text-sm text-[var(--accent)]">
            View all
          </Link>
        </div>
        {favorites.data && favorites.data.length > 0 ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {favorites.data.slice(0, 6).map((fav, index) => (
              <ToolCard
                key={fav.id}
                slug={fav.tool.slug}
                category={fav.tool.category}
                name={asLocalized(fav.tool.name)}
                description={asLocalized(fav.tool.description)}
                locale={locale}
                premium={fav.tool.premium}
                index={index}
              />
            ))}
          </div>
        ) : (
          <p className="text-sm text-[var(--muted)]">{t("emptyFavorites")}</p>
        )}
      </section>

      <section>
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="font-display text-xl font-semibold">{t("history")}</h2>
          <Link href="/history" className="text-sm text-[var(--accent)]">
            View all
          </Link>
        </div>
        {history.data && history.data.length > 0 ? (
          <ul className="divide-y divide-[var(--border)] surface overflow-hidden rounded-[var(--radius-lg)]">
            {history.data.slice(0, 10).map((item) => (
              <li key={item.id}>
                <Link
                  href={`/tools/${item.tool.category}/${item.tool.slug}`}
                  className="flex items-center justify-between gap-3 px-4 py-3 hover:bg-[color-mix(in_oklab,var(--accent)_8%,transparent)]"
                >
                  <span className="text-sm font-medium">
                    {localize(item.tool.name, locale)}
                  </span>
                  <span className="text-xs text-[var(--muted)]">
                    {new Date(item.created_at).toLocaleString(locale)}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-[var(--muted)]">{t("emptyHistory")}</p>
        )}
      </section>
    </div>
  );
}

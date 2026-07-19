"use client";

import { useQuery } from "@tanstack/react-query";
import { useLocale, useTranslations } from "next-intl";
import { api } from "@/lib/api";
import { useAuth } from "@/features/auth/auth-context";
import { ToolCard } from "@/components/ToolCard";
import { Link } from "@/i18n/navigation";
import { Button } from "@/components/ui/button";

function asLocalized(value: string | Record<string, string>) {
  if (typeof value === "string") return value;
  return {
    en: value.en ?? Object.values(value)[0] ?? "",
    ar: value.ar,
  };
}

export default function FavoritesPage() {
  const t = useTranslations("dashboard");
  const locale = useLocale();
  const { user, isLoading } = useAuth();
  const favorites = useQuery({
    queryKey: ["favorites"],
    queryFn: () => api.favorites(),
    enabled: Boolean(user),
  });

  if (isLoading) return <div className="p-8">…</div>;
  if (!user) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-16">
        <Button asChild>
          <Link href="/auth/login">Log in</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-3xl font-semibold">{t("favorites")}</h1>
      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {(favorites.data ?? []).map((fav, index) => (
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
      {(favorites.data ?? []).length === 0 ? (
        <p className="mt-6 text-sm text-[var(--muted)]">{t("emptyFavorites")}</p>
      ) : null}
    </div>
  );
}

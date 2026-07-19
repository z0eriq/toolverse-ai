"use client";

import { useQuery } from "@tanstack/react-query";
import { useLocale, useTranslations } from "next-intl";
import { api } from "@/lib/api";
import { useAuth } from "@/features/auth/auth-context";
import { Link } from "@/i18n/navigation";
import { Button } from "@/components/ui/button";
import { localize } from "@/lib/utils";

export default function HistoryPage() {
  const t = useTranslations("dashboard");
  const locale = useLocale();
  const { user, isLoading } = useAuth();
  const history = useQuery({
    queryKey: ["history"],
    queryFn: () => api.history(),
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
      <h1 className="font-display text-3xl font-semibold">{t("history")}</h1>
      {(history.data ?? []).length === 0 ? (
        <p className="mt-6 text-sm text-[var(--muted)]">{t("emptyHistory")}</p>
      ) : (
        <ul className="mt-8 divide-y divide-[var(--border)] surface overflow-hidden rounded-[var(--radius-lg)]">
          {(history.data ?? []).map((item) => (
            <li key={item.id}>
              <Link
                href={`/tools/${item.tool.category}/${item.tool.slug}`}
                className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 hover:bg-[color-mix(in_oklab,var(--accent)_8%,transparent)]"
              >
                <div>
                  <p className="text-sm font-medium">
                    {localize(item.tool.name, locale)}
                  </p>
                  <p className="text-xs text-[var(--muted)]">{item.action}</p>
                </div>
                <time className="text-xs text-[var(--muted)]">
                  {new Date(item.created_at).toLocaleString(locale)}
                </time>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

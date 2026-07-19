"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { ApiError, api, type ApiKeyItem } from "@/lib/api";
import { useAuth } from "@/features/auth/auth-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link } from "@/i18n/navigation";
import { copyToClipboard } from "@/lib/utils";

export function ApiKeysPanel() {
  const t = useTranslations("developers");
  const { user, isLoading } = useAuth();
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const keys = useQuery({
    queryKey: ["marketplace-api-keys"],
    queryFn: () => api.listApiKeys(),
    enabled: Boolean(user),
    retry: false,
  });

  const usage = useQuery({
    queryKey: ["marketplace-api-usage"],
    queryFn: () => api.apiUsage(),
    enabled: Boolean(user),
    retry: false,
  });

  const createMutation = useMutation({
    mutationFn: () => api.createApiKey({ name: name.trim() || "Default" }),
    onSuccess: async (data) => {
      setError(null);
      setCreatedKey(data.key ?? null);
      setName("");
      await queryClient.invalidateQueries({ queryKey: ["marketplace-api-keys"] });
      await queryClient.invalidateQueries({ queryKey: ["marketplace-api-usage"] });
    },
    onError: (err) => {
      setError(err instanceof ApiError ? err.message : t("createError"));
    },
  });

  const revokeMutation = useMutation({
    mutationFn: (id: number) => api.revokeApiKey(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["marketplace-api-keys"] });
      await queryClient.invalidateQueries({ queryKey: ["marketplace-api-usage"] });
    },
  });

  if (isLoading) {
    return <p className="text-sm text-[var(--muted)]">{t("loading")}</p>;
  }

  if (!user) {
    return (
      <Card>
        <h2 className="font-display text-xl font-semibold">{t("keysTitle")}</h2>
        <p className="mt-2 text-sm text-[var(--muted)]">{t("loginRequired")}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button asChild>
            <Link href="/auth/login">{t("login")}</Link>
          </Button>
          <Button asChild variant="secondary">
            <Link href="/auth/register">{t("register")}</Link>
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <h2 className="font-display text-xl font-semibold">{t("keysTitle")}</h2>
        <p className="mt-1 text-sm text-[var(--muted)]">{t("keysSupporting")}</p>

        <form
          className="mt-6 flex flex-wrap items-end gap-3"
          onSubmit={(e) => {
            e.preventDefault();
            setCreatedKey(null);
            createMutation.mutate();
          }}
        >
          <div className="min-w-[220px] flex-1">
            <Label htmlFor="api-key-name">{t("keyName")}</Label>
            <Input
              id="api-key-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t("keyNamePlaceholder")}
              required
            />
          </div>
          <Button type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending ? t("creating") : t("createKey")}
          </Button>
        </form>

        {error ? (
          <p className="mt-3 text-sm text-[var(--color-danger)]" role="alert">
            {error}
          </p>
        ) : null}

        {createdKey ? (
          <div
            className="mt-4 rounded-[var(--radius-md)] border border-[var(--accent)]/40 bg-[color-mix(in_oklab,var(--accent)_10%,transparent)] p-4"
            role="status"
          >
            <p className="text-sm font-medium">{t("keyOnce")}</p>
            <code className="mt-2 block break-all font-mono text-sm">{createdKey}</code>
            <Button
              type="button"
              size="sm"
              variant="secondary"
              className="mt-3"
              onClick={async () => {
                const ok = await copyToClipboard(createdKey);
                if (ok) {
                  setCopied(true);
                  window.setTimeout(() => setCopied(false), 1600);
                }
              }}
            >
              {copied ? t("copied") : t("copyKey")}
            </Button>
          </div>
        ) : null}
      </Card>

      {usage.data ? (
        <Card>
          <h3 className="font-display text-lg font-semibold">{t("usageTitle")}</h3>
          <dl className="mt-4 grid gap-3 sm:grid-cols-3">
            <div>
              <dt className="text-xs uppercase text-[var(--muted)]">{t("keysActive")}</dt>
              <dd className="mt-1 font-display text-2xl tabular-nums">
                {usage.data.keys_active}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase text-[var(--muted)]">{t("usageMonth")}</dt>
              <dd className="mt-1 font-display text-2xl tabular-nums">
                {usage.data.usage_this_month}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase text-[var(--muted)]">{t("totalCalls")}</dt>
              <dd className="mt-1 font-display text-2xl tabular-nums">
                {usage.data.total_calls}
              </dd>
            </div>
          </dl>
        </Card>
      ) : null}

      <Card>
        <h3 className="font-display text-lg font-semibold">{t("keysList")}</h3>
        {keys.isLoading ? (
          <p className="mt-3 text-sm text-[var(--muted)]">{t("loading")}</p>
        ) : null}
        {keys.isError ? (
          <p className="mt-3 text-sm text-[var(--color-danger)]">{t("loadError")}</p>
        ) : null}
        <ul className="mt-4 divide-y divide-[var(--border)]">
          {(keys.data ?? []).map((key: ApiKeyItem) => (
            <li
              key={key.id}
              className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm"
            >
              <div>
                <p className="font-medium">{key.name}</p>
                <p className="mt-1 font-mono text-xs text-[var(--muted)]">
                  {key.key_prefix}… · {key.rate_limit_per_minute}/min ·{" "}
                  {key.usage_this_month}/{key.monthly_quota}
                  {key.revoked_at ? ` · ${t("revoked")}` : ""}
                </p>
              </div>
              {!key.revoked_at ? (
                <Button
                  type="button"
                  size="sm"
                  variant="danger"
                  disabled={revokeMutation.isPending}
                  onClick={() => revokeMutation.mutate(key.id)}
                >
                  {t("revoke")}
                </Button>
              ) : null}
            </li>
          ))}
        </ul>
        {keys.data?.length === 0 ? (
          <p className="mt-3 text-sm text-[var(--muted)]">{t("keysEmpty")}</p>
        ) : null}
      </Card>
    </div>
  );
}

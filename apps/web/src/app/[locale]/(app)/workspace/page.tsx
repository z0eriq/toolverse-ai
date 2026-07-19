"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/features/auth/auth-context";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link } from "@/i18n/navigation";
import { cn } from "@/lib/utils";

type WorkspaceTab = "saved" | "collections";

export default function WorkspacePage() {
  const t = useTranslations("workspace");
  const { user, isLoading } = useAuth();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<WorkspaceTab>("saved");
  const [collectionName, setCollectionName] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const saved = useQuery({
    queryKey: ["saved-outputs"],
    queryFn: () => api.savedOutputs(),
    enabled: Boolean(user) && tab === "saved",
  });

  const collections = useQuery({
    queryKey: ["collections"],
    queryFn: () => api.collections(),
    enabled: Boolean(user) && tab === "collections",
  });

  const createCollection = useMutation({
    mutationFn: () =>
      api.createCollection({
        name: collectionName.trim(),
        slug: collectionName
          .trim()
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/^-|-$/g, ""),
      }),
    onSuccess: async () => {
      setCollectionName("");
      setFormError(null);
      await queryClient.invalidateQueries({ queryKey: ["collections"] });
    },
    onError: (err) => {
      setFormError(err instanceof ApiError ? err.message : t("createError"));
    },
  });

  const deleteSaved = useMutation({
    mutationFn: (id: number) => api.deleteSavedOutput(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["saved-outputs"] });
    },
  });

  const deleteCollection = useMutation({
    mutationFn: (slug: string) => api.deleteCollection(slug),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["collections"] });
    },
  });

  const tabs = useMemo(
    () =>
      [
        { id: "saved" as const, label: t("tabSaved") },
        { id: "collections" as const, label: t("tabCollections") },
      ] satisfies { id: WorkspaceTab; label: string }[],
    [t],
  );

  if (isLoading) {
    return <div className="p-8">{t("loading")}</div>;
  }

  if (!user) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h1 className="font-display text-3xl font-semibold">{t("title")}</h1>
        <p className="mt-2 text-[var(--muted)]">{t("loginRequired")}</p>
        <Button asChild className="mt-6">
          <Link href="/auth/login">{t("login")}</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      <h1 className="font-display text-3xl font-semibold tracking-tight">
        {t("title")}
      </h1>
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

      {tab === "saved" ? (
        <div className="mt-8 space-y-4">
          {(saved.data ?? []).length === 0 ? (
            <p className="text-sm text-[var(--muted)]">{t("emptySaved")}</p>
          ) : null}
          {(saved.data ?? []).map((item) => (
            <Card key={item.id} className="flex flex-wrap items-start justify-between gap-4">
              <div className="min-w-0 flex-1">
                <p className="font-medium">{item.title || t("untitled")}</p>
                <p className="mt-1 font-mono text-xs text-[var(--muted)]">
                  {item.tool_slug}
                </p>
                <pre className="mt-3 max-h-40 overflow-auto whitespace-pre-wrap break-words text-xs text-[var(--muted)]">
                  {typeof item.content === "string"
                    ? item.content
                    : JSON.stringify(item.content, null, 2)}
                </pre>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => deleteSaved.mutate(item.id)}
                disabled={deleteSaved.isPending}
              >
                {t("delete")}
              </Button>
            </Card>
          ))}
        </div>
      ) : null}

      {tab === "collections" ? (
        <div className="mt-8 space-y-6">
          <Card>
            <form
              className="flex flex-wrap items-end gap-3"
              onSubmit={(e) => {
                e.preventDefault();
                if (!collectionName.trim()) return;
                createCollection.mutate();
              }}
            >
              <div className="min-w-[12rem] flex-1">
                <Label htmlFor="collection-name">{t("newCollection")}</Label>
                <Input
                  id="collection-name"
                  value={collectionName}
                  onChange={(e) => setCollectionName(e.target.value)}
                  placeholder={t("collectionPlaceholder")}
                  required
                />
              </div>
              <Button type="submit" disabled={createCollection.isPending}>
                {createCollection.isPending ? t("creating") : t("create")}
              </Button>
            </form>
            {formError ? (
              <p className="mt-3 text-sm text-[var(--color-danger)]" role="alert">
                {formError}
              </p>
            ) : null}
          </Card>

          {(collections.data ?? []).length === 0 ? (
            <p className="text-sm text-[var(--muted)]">{t("emptyCollections")}</p>
          ) : null}

          <div className="grid gap-4 sm:grid-cols-2">
            {(collections.data ?? []).map((collection) => (
              <Card key={collection.id}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="font-display text-lg font-semibold">
                      {collection.name}
                    </h2>
                    {collection.description ? (
                      <p className="mt-1 text-sm text-[var(--muted)]">
                        {collection.description}
                      </p>
                    ) : null}
                    <p className="mt-2 text-xs text-[var(--muted)]">
                      {t("itemCount", { count: collection.items?.length ?? 0 })}
                    </p>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteCollection.mutate(collection.slug)}
                    disabled={deleteCollection.isPending}
                  >
                    {t("delete")}
                  </Button>
                </div>
                {collection.items?.length ? (
                  <ul className="mt-4 space-y-1 text-sm">
                    {collection.items.map((item) => (
                      <li key={item.id} className="font-mono text-xs">
                        {item.tool_slug}
                      </li>
                    ))}
                  </ul>
                ) : null}
              </Card>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
